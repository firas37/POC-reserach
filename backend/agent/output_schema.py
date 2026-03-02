"""
Zyga Research & Enrichment Agent — Output Schema
Pydantic model that the agent's JSON output is parsed into.

NOTE: All fields that may be absent use explicit empty defaults (not None)
so that mcp-use does NOT treat them as required during schema validation.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class AgentOutput(BaseModel):
    """Structured output produced by the research agent."""

    # Core identity — always populated
    name: str = ""
    title: str = ""
    company: str = ""

    # Company info — best-effort, may be empty
    company_size: str = ""
    industry: str = ""

    # ICP scoring — always populated
    icp_score: int = Field(0, ge=0, le=100)
    icp_reasoning: str = ""

    # ── Final Output ─────────────────────────────────────────
    research_summary: str = Field(
        default="",
        description="2-3 sentence summary uniting the person and the company's current context."
    )
    personalization_hooks: List[str] = Field(
        default_factory=list,
        description="List of 2-3 specific angles or hooks for cold outreach."
    )
    recommended_action: str = Field(
        default="",
        description="Clear next step (e.g. 'Highly qualified — reach out immediately', 'Skip, too small')."
    )
    tools_used: List[str] = Field(
        default_factory=list,
        description="Names of the MCP tools actually called during this run."
    )
