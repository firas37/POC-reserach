import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.getcwd())

from backend.mcp_servers.fullenrich.client import FullEnrichClient
from backend.config import settings

async def test_enrich():
    print(f"Testing FullEnrich with API Key: {settings.FULLENRICH_API_KEY[:5]}...{settings.FULLENRICH_API_KEY[-5:]}")
    client = FullEnrichClient()
    try:
        result = await client.enrich(
            first_name="Alex",
            last_name="Rivera",
            domain="rippling.com"
        )
        print("Enrichment Succeeded!")
        print(result)
    except Exception as e:
        print("Enrichment Failed with Exception:")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_enrich())
