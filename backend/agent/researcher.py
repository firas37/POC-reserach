"""
Zyga Research & Enrichment Agent — Main Agent Logic
Uses mcp-use to bridge GPT-5 (GitHub Models) with MCP servers (Linkup + FullEnrich).
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
    Attempts JSON extraction; falls back to defaults on failure.
    """
    # Try to extract JSON from the raw text
    json_match = re.search(r"\{[\s\S]*\}", raw_text)
    if json_match:
        try:
            data = json.loads(json_match.group())
            # Validate through Pydantic
            output = AgentOutput(**data)
            return output.model_dump()
        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"JSON parse failed, using fallback: {e}")

    # Fallback: return a minimal result with the raw text
    return AgentOutput(
        name=f"{prospect.get('first_name', '')} {prospect.get('last_name', '')}".strip(),
        company=prospect.get("company", "Unknown"),
        title=prospect.get("title"),
        icp_score=0,
        icp_reasoning="Agent output could not be parsed into structured format.",
        research_summary=raw_text[:500] if raw_text else "No response from agent.",
        recommended_action="Retry research — agent output was not structured.",
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

    # ── Configure LLM (GPT-5 via GitHub Models) ─────────────
    llm = ChatOpenAI(
        base_url=settings.GITHUB_MODELS_ENDPOINT,
        api_key=settings.GITHUB_TOKEN,
        model=settings.GPT5_MODEL_NAME,
    )

    # ── Create MCP Agent ─────────────────────────────────────
    agent = MCPAgent(
        llm=llm,
        client=client,
        max_steps=15,
        system_prompt=SYSTEM_PROMPT,
    )

    # ── Build the user message ───────────────────────────────
    user_message = f"""
Research and qualify this prospect:
Name: {prospect['first_name']} {prospect['last_name']}
Title: {prospect.get('title', 'Unknown')}
Company: {prospect['company']}
Domain: {prospect.get('domain', '')}
LinkedIn: {prospect.get('linkedin_url', '')}

Return a complete JSON profile with ICP score, research summary,
personalization hooks, and enriched contact data if score >= {settings.ICP_MIN_SCORE_FOR_ENRICHMENT}.
"""

    try:
        # ── Run agent ────────────────────────────────────────
        logger.info("Agent loop starting...")
        result = await agent.run(user_message)
        logger.info("Agent loop completed.")

        # ── Parse output ─────────────────────────────────────
        parsed = _parse_agent_output(result, prospect)
        logger.info(f"ICP score: {parsed.get('icp_score', 'N/A')}")
        return parsed

    except Exception as e:
        logger.error(f"Agent execution failed: {e}")
        return AgentOutput(
            name=f"{prospect.get('first_name', '')} {prospect.get('last_name', '')}".strip(),
            company=prospect.get("company", "Unknown"),
            title=prospect.get("title"),
            icp_score=0,
            icp_reasoning=f"Agent error: {str(e)}",
            recommended_action="Check API keys and retry.",
        ).model_dump()

    finally:
        # Always clean up MCP client connections
        try:
            await client.close()
        except Exception:
            pass
