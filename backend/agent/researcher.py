"""
Zyga Research & Enrichment Agent — Main Agent Logic
Uses mcp-use to bridge the LLM (via GitHub Models) with MCP servers (Linkup + FullEnrich).
"""

import json
import re
import sys
from pathlib import Path

from mcp_use import MCPAgent, MCPClient
from langchain_openai import ChatOpenAI

from backend.config import settings
from backend.agent.prompts import SYSTEM_PROMPT
from backend.agent.output_schema import AgentOutput
from backend.utils.logger import get_logger

logger = get_logger(__name__)


def _build_mcp_config() -> dict:
    """Build the MCP server configuration dictionary."""
    # Resolve the project root for the FullEnrich server path
    project_root = Path(__file__).resolve().parent.parent.parent

    return {
        "mcpServers": {
            "linkup": {
                "command": sys.executable,
                "args": ["-m", "backend.mcp_servers.linkup.server"],
                "env": {
                    "LINKUP_API_KEY": settings.LINKUP_API_KEY,
                },
            },
            "fullenrich": {
                "command": sys.executable,
                "args": ["-m", "backend.mcp_servers.fullenrich.server"],
                "env": {
                    "FULLENRICH_API_KEY": settings.FULLENRICH_API_KEY,
                    "FULLENRICH_API_BASE": settings.FULLENRICH_API_BASE,
                },
            },
        }
    }


def _parse_agent_output(raw_text: str, prospect: dict) -> dict:
    """
    Parse the agent's raw text response into a structured dictionary.
    Tries multiple JSON extraction strategies before falling back to defaults.
    """
    if not raw_text:
        return _fallback_output(prospect, "No response from agent.")

    # Strategy 1: direct JSON parse
    try:
        data = json.loads(raw_text.strip())
        return _validate_and_coerce(data, prospect)
    except (json.JSONDecodeError, ValueError):
        pass

    # Strategy 2: extract first {...} block (handles markdown fences or extra text)
    json_match = re.search(r"\{[\s\S]*\}", raw_text)
    if json_match:
        try:
            data = json.loads(json_match.group())
            return _validate_and_coerce(data, prospect)
        except (json.JSONDecodeError, ValueError):
            pass

    # Strategy 3: find JSON after known markers
    for marker in ["```json", "```", "\n{"]:
        idx = raw_text.find(marker)
        if idx != -1:
            snippet = raw_text[idx:].lstrip("`json").lstrip("`").strip()
            try:
                data = json.loads(snippet.split("```")[0].strip())
                return _validate_and_coerce(data, prospect)
            except (json.JSONDecodeError, ValueError):
                pass

    logger.warning(f"All JSON parse strategies failed. Raw: {raw_text[:200]}")
    return _fallback_output(prospect, f"Agent output could not be parsed. Raw: {raw_text[:500]}")


def _validate_and_coerce(data: dict, prospect: dict) -> dict:
    """Validate parsed dict through Pydantic and coerce types."""
    # Merge prospect identity in case agent omitted them
    data.setdefault("name", f"{prospect.get('first_name', '')} {prospect.get('last_name', '')}".strip())
    data.setdefault("company", prospect.get("company", ""))
    data.setdefault("title", prospect.get("title", ""))

    # Coerce null → empty string for string fields
    for field in ("email", "phone", "research_summary", "company_size", "industry",
                  "icp_reasoning", "recommended_action"):
        if data.get(field) is None:
            data[field] = ""

    # Coerce null → empty list for list fields
    for field in ("personalization_hooks", "tools_used"):
        if data.get(field) is None:
            data[field] = []

    output = AgentOutput(**{k: v for k, v in data.items() if k in AgentOutput.model_fields})
    return output.model_dump()


def _fallback_output(prospect: dict, reason: str) -> dict:
    """Return a minimal fallback output when parsing fails."""
    return AgentOutput(
        name=f"{prospect.get('first_name', '')} {prospect.get('last_name', '')}".strip(),
        company=prospect.get("company", "Unknown"),
        title=prospect.get("title", ""),
        icp_score=0,
        icp_reasoning=f"Agent error: {reason}",
        recommended_action="Check API keys and retry.",
    ).model_dump()


async def run_research_agent(prospect: dict) -> dict:
    """
    Run the Research & Enrichment Agent for a given prospect.

    Args:
        prospect: Dict with keys first_name, last_name, company, title,
                  linkedin_url (optional), domain (optional).

    Returns:
        Structured dict matching AgentOutput schema.
    """
    logger.info(
        f"Starting research for {prospect.get('first_name')} "
        f"{prospect.get('last_name')} at {prospect.get('company')}"
    )

    # ── Build MCP configuration ──────────────────────────────
    mcp_config = _build_mcp_config()

    # ── Create MCP client ────────────────────────────────────
    client = MCPClient(mcp_config)

    # ── Configure LLM (via GitHub Models) ───────────────────
    llm = ChatOpenAI(
        base_url=settings.GITHUB_MODELS_ENDPOINT,
        api_key=settings.GITHUB_TOKEN,
        model=settings.GPT5_MODEL_NAME,
    )

    # ── Create MCP Agent ─────────────────────────────────────
    # IMPORTANT: recursion_limit = max_steps * 2 (set by mcp-use internals).
    # LangGraph counts every graph node (agent + tool), not just tool calls.
    # With 3-4 tool calls the graph traverses ~8-10 nodes, so recursion_limit
    # must be > 10. Setting max_steps=15 gives recursion_limit=30, well above
    # LangGraph's default 20 cap, while the prompt still enforces <=4 tool calls.
    agent = MCPAgent(
        llm=llm,
        client=client,
        max_steps=15,
        system_prompt=SYSTEM_PROMPT,
        verbose=False,
    )

    # ── Build the user message ───────────────────────────────
    user_message = f"""
Research and qualify this prospect:
Name: {prospect['first_name']} {prospect['last_name']}
Title: {prospect.get('title', 'Unknown')}
Company: {prospect['company']}
Domain: {prospect.get('domain', '')}
LinkedIn: {prospect.get('linkedin_url', '')}

Use the ICP point system from your instructions to compute an exact score.
Return ONLY the JSON object — no markdown fences, no extra text.
Enrich contact data only if ICP score >= {settings.ICP_MIN_SCORE_FOR_ENRICHMENT}.
"""

    try:
        # ── Run agent (no output_schema — we parse ourselves) ─
        logger.info("Agent loop starting...")
        # NOTE: We intentionally do NOT pass output_schema=AgentOutput here.
        # The mcp-use library's structured output validation is overly strict and
        # crashes when optional fields (email, phone) are returned as null.
        # We use our own robust _parse_agent_output() instead.
        result = await agent.run(user_message)
        logger.info("Agent loop completed.")

        # ── Parse output ─────────────────────────────────────
        parsed = _parse_agent_output(result, prospect)
        logger.info(f"ICP score: {parsed.get('icp_score', 'N/A')} — {parsed.get('name')}")
        return parsed

    except Exception as e:
        logger.error(f"Agent execution failed: {e}")
        return _fallback_output(prospect, str(e))

    finally:
        # Always clean up MCP client connections
        try:
            await client.close()
        except Exception:
            pass
