"""
Zyga Research & Enrichment Agent — API Routes
"""

from fastapi import APIRouter, HTTPException
from backend.api.models import ProspectRequest, ResearchResponse, HealthResponse
from backend.agent.researcher import run_research_agent
from backend.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse()


@router.post("/research", response_model=ResearchResponse)
async def research_prospect(prospect: ProspectRequest):
    """
    Research and qualify a prospect.

    Runs the Research & Enrichment Agent which:
    1. Searches for the prospect using Linkup (standard/deep)
    2. Scores against ICP criteria
    3. Enriches with FullEnrich if score >= threshold
    4. Returns structured qualification report
    """
    logger.info(
        f"Research request: {prospect.first_name} {prospect.last_name} "
        f"at {prospect.company}"
    )

    try:
        result = await run_research_agent(prospect.model_dump())
        return ResearchResponse(**result)

    except Exception as e:
        logger.error(f"Research endpoint error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Research agent failed: {str(e)}",
        )
