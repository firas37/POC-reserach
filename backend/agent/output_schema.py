"""
Zyga Research & Enrichment Agent — Output Schema
Pydantic model that the agent's JSON output is parsed into.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class AgentOutput(BaseModel):
    """Structured output produced by the research agent."""

    name: str = ""
    title: Optional[str] = None
    company: str = ""
    company_size: Optional[str] = None
    industry: Optional[str] = None
    icp_score: int = Field(0, ge=0, le=100)
    icp_reasoning: str = ""
    email: Optional[str] = None
    phone: Optional[str] = None
    research_summary: Optional[str] = None
    personalization_hooks: List[str] = Field(default_factory=list)
    recommended_action: Optional[str] = None
    tools_used: List[str] = Field(default_factory=list)
    enrichment_triggered: bool = False
    credits_used: int = 0
