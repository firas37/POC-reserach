"""
FullEnrich REST API Client
Wraps the FullEnrich API for contact enrichment and credit checking.
"""

import asyncio
import httpx
from backend.config import settings
from backend.utils.logger import get_logger

logger = get_logger(__name__)

# Polling configuration
POLL_INTERVAL_SECONDS = 3
POLL_MAX_ATTEMPTS = 40  # ~2 minutes max


class FullEnrichClient:
    """Async client for the FullEnrich REST API."""

    def __init__(self):
        self.base_url = settings.FULLENRICH_API_BASE
        self.headers = {
            "Authorization": f"Bearer {settings.FULLENRICH_API_KEY}",
            "Content-Type": "application/json",
        }

    async def enrich(
        self,
        first_name: str,
        last_name: str,
        domain: str,
        linkedin_url: str | None = None,
    ) -> dict:
        """
        Start a bulk enrichment job for a single contact and poll for results.

        Returns:
            Dict with email, phone, and confidence_score fields.
        """
        contact = {
            "firstname": first_name,
            "lastname": last_name,
            "domain": domain,
        }
        if linkedin_url:
            contact["linkedin_url"] = linkedin_url

        payload = {"contacts": [contact]}

        async with httpx.AsyncClient(timeout=30.0) as client:
            # Start enrichment job
            logger.info(f"Starting enrichment for {first_name} {last_name} @ {domain}")
            resp = await client.post(
                f"{self.base_url}/contact/enrich/bulk",
                json=payload,
                headers=self.headers,
            )
            resp.raise_for_status()
            enrichment_id = resp.json()["id"]
            logger.info(f"Enrichment job started: {enrichment_id}")

            # Poll for result
            return await self._poll_result(client, enrichment_id)

    async def _poll_result(self, client: httpx.AsyncClient, enrichment_id: str) -> dict:
        """Poll FullEnrich API until the enrichment job completes."""
        for attempt in range(POLL_MAX_ATTEMPTS):
            await asyncio.sleep(POLL_INTERVAL_SECONDS)

            resp = await client.get(
                f"{self.base_url}/bulk/{enrichment_id}",
                headers=self.headers,
            )
            resp.raise_for_status()
            data = resp.json()

            status = data.get("status", "pending")
            logger.debug(f"Poll attempt {attempt + 1}: status={status}")

            if status == "completed":
                contacts = data.get("contacts", [])
                if contacts:
                    contact = contacts[0]
                    return {
                        "email": contact.get("email"),
                        "phone": contact.get("phone"),
                        "confidence_score": contact.get("confidence_score", 0),
                    }
                return {"email": None, "phone": None, "confidence_score": 0}

            if status == "failed":
                logger.error(f"Enrichment job {enrichment_id} failed")
                return {"email": None, "phone": None, "confidence_score": 0, "error": "Enrichment failed"}

        logger.warning(f"Enrichment job {enrichment_id} timed out after polling")
        return {"email": None, "phone": None, "confidence_score": 0, "error": "Timeout"}

    async def get_credits(self) -> dict:
        """Check remaining FullEnrich API credits."""
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(
                f"{self.base_url}/account/credits",
                headers=self.headers,
            )
            resp.raise_for_status()
            return resp.json()
