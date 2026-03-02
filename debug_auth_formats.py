import asyncio
import httpx
import os
import sys

# Add project root to path
sys.path.append(os.getcwd())

from backend.config import settings

async def test_auth_formats():
    key = settings.FULLENRICH_API_KEY
    base_url = settings.FULLENRICH_API_BASE
    endpoint = f"{base_url}/account/credits"
    
    formats = [
        ("Bearer Token", {"Authorization": f"Bearer {key}"}),
        ("X-API-Key", {"X-API-Key": key}),
        ("Raw Authorization", {"Authorization": key}),
    ]
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        for name, headers in formats:
            print(f"Testing {name}...")
            try:
                resp = await client.get(endpoint, headers=headers)
                print(f"  Status: {resp.status_code}")
                if resp.status_code == 200:
                    print(f"  SUCCESS! {name} works.")
                    print(f"  Result: {resp.json()}")
                    return
                else:
                    print(f"  Failed: {resp.text[:100]}")
            except Exception as e:
                print(f"  Error: {e}")
    
    print("\nNone of the formats worked. The key might be invalid or restricted.")

if __name__ == "__main__":
    asyncio.run(test_auth_formats())
