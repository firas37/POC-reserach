"""
Zyga Research & Enrichment Agent — API Routes
"""

import traceback
from fastapi import APIRouter, HTTPException
from backend.api.models import ProspectRequest, ResearchResponse, HealthResponse, EnrichRequest, EnrichResponse
from backend.agent.researcher import run_research_agent
from backend.mcp_servers.fullenrich.client import FullEnrichClient
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

    Runs the Research Agent which:
    1. Searches for the prospect using Linkup (standard/deep)
    2. Scores against ICP criteria
    3. Returns structured qualification report
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
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail="Research agent encountered an error. Please try again.",
        )


@router.post("/enrich", response_model=EnrichResponse)
async def enrich_prospect(prospect: EnrichRequest):
    """
    Enrich a qualified prospect using FullEnrich.
    Called directly by the UI when the user decides to unlock contact info.
    """
    logger.info(f"Enrichment request: {prospect.first_name} {prospect.last_name} at {prospect.domain}")
    
    try:
        client = FullEnrichClient()
        result = await client.enrich(
            first_name=prospect.first_name,
            last_name=prospect.last_name,
            domain=prospect.domain,
            linkedin_url=prospect.linkedin_url
        )
        return EnrichResponse(**result)
        
    except Exception as e:
        logger.error(f"Enrichment endpoint error: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail="Enrichment service encountered an error. Please try again.",
        )
