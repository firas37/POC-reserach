import asyncio
import httpx
import os
import sys

sys.path.append(os.getcwd())
from backend.config import settings

async def test_endpoints():
    key = settings.FULLENRICH_API_KEY
    print(f"Key: '{key}'")
    print(f"Key length: {len(key)}")
    print()
    
    # Test multiple base URLs and endpoints
    tests = [
        ("v2 credits", "GET", "https://app.fullenrich.com/api/v2/account/credits"),
        ("v1 credits", "GET", "https://app.fullenrich.com/api/v1/account/credits"),
        ("no version credits", "GET", "https://app.fullenrich.com/api/account/credits"),
        ("v2 enrich bulk", "POST", "https://app.fullenrich.com/api/v2/contact/enrich/bulk"),
        ("v1 enrich bulk", "POST", "https://app.fullenrich.com/api/v1/contact/enrich/bulk"),
    ]
    
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }
    
    payload = {"contacts": [{"firstname": "Alex", "lastname": "Rivera", "domain": "rippling.com"}]}
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        for name, method, url in tests:
            print(f"Testing {name}: {method} {url}")
            try:
                if method == "GET":
                    resp = await client.get(url, headers=headers)
                else:
                    resp = await client.post(url, headers=headers, json=payload)
                print(f"  Status: {resp.status_code}")
                print(f"  Response: {resp.text[:200]}")
            except Exception as e:
                print(f"  Error: {e}")
            print()

if __name__ == "__main__":
    asyncio.run(test_endpoints())
