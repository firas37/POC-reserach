import httpx
import os
from mcp.server.fastmcp import FastMCP
from typing import Optional, Dict, Any

# Initialize FastMCP server
mcp = FastMCP("ZygaLinkup")

LINKUP_API_KEY = os.getenv("LINKUP_API_KEY")
LINKUP_API_BASE = "https://api.linkup.so/v1"

@mcp.tool()
async def linkup_search(
    query: str,
    depth: str = "standard",
    outputType: str = "searchResults",
) -> str:
    """
    Search the web using Linkup API for up-to-date information.
    
    Args:
        query: The search query.
        depth: "standard" (faster) or "deep" (more comprehensive, costs more credits).
        outputType: Format of results, usually "searchResults" or "sourcedAnswer".
    """
    if not LINKUP_API_KEY:
        return "Error: LINKUP_API_KEY is missing."
        
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{LINKUP_API_BASE}/search",
                headers={
                    "Authorization": f"Bearer {LINKUP_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "q": query,
                    "depth": depth,
                    "outputType": outputType
                },
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()
            
            # Format results into a readable string
            if "results" in data:
                formatted = [f"- {r.get('name', '')}\n  {r.get('snippet', '')}\n  URL: {r.get('url', '')}" for r in data["results"][:5]]
                return "\n\n".join(formatted)
            elif "answer" in data:
                return data["answer"]
            return str(data)
            
        except httpx.HTTPStatusError as e:
            return f"Linkup Search API Error: {e.response.status_code} - {e.response.text}"
        except Exception as e:
            return f"Linkup Search Error: {str(e)}"

if __name__ == "__main__":
    mcp.run()
