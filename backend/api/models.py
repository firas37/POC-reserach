"""
Zyga Research & Enrichment Agent — API Request / Response Models
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class ProspectRequest(BaseModel):
    """Incoming prospect data for research & qualification."""

    first_name: str = Field(..., description="Prospect's first name")
    last_name: str = Field(..., description="Prospect's last name")
    company: str = Field(..., description="Company name")
    title: Optional[str] = Field(None, description="Job title")
    linkedin_url: Optional[str] = Field(None, description="LinkedIn profile URL")
    domain: Optional[str] = Field(None, description="Company domain (e.g. notion.so)")


class ResearchResponse(BaseModel):
    """Structured output returned by the research agent."""

    name: str
    title: Optional[str] = None
    company: str
    company_size: Optional[str] = None
    industry: Optional[str] = None
    icp_score: int = Field(..., ge=0, le=100)
    icp_reasoning: str
    email: Optional[str] = None
    phone: Optional[str] = None
    research_summary: Optional[str] = None
    personalization_hooks: List[str] = Field(default_factory=list)
    recommended_action: Optional[str] = None
    tools_used: List[str] = Field(default_factory=list)
    enrichment_triggered: bool = False
    credits_used: int = 0


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = "ok"
    service: str = "zyga-research-poc"
