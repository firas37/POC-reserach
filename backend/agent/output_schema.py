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

    # Contact data — only populated after enrichment
    email: str = ""
    phone: str = ""

    # Research output — populated after research
    research_summary: str = ""
    personalization_hooks: List[str] = Field(default_factory=list)
    recommended_action: str = ""

    # Metadata
    tools_used: List[str] = Field(default_factory=list)
    enrichment_triggered: bool = False
    credits_used: int = 0
