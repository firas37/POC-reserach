import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.getcwd())

from backend.mcp_servers.fullenrich.client import FullEnrichClient
from backend.config import settings

async def test_credits():
    print(f"Checking credits with API Key: {settings.FULLENRICH_API_KEY[:5]}...{settings.FULLENRICH_API_KEY[-5:]}")
    client = FullEnrichClient()
    try:
        result = await client.get_credits()
        print("Credit Check Succeeded!")
        print(result)
    except Exception as e:
        print("Credit Check Failed with Exception:")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_credits())
