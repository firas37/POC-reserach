"""
FullEnrich Custom MCP Server
Built with FastMCP — exposes enrich_contact and check_credits as MCP tools.

The ICP credit-gating rule lives in the tool description:
"Only call this tool if the prospect's ICP score is >= 60"
This allows GPT-5 to enforce the business rule autonomously.

Run:  python -m backend.mcp_servers.fullenrich.server
"""

from fastmcp import FastMCP
from backend.mcp_servers.fullenrich.client import FullEnrichClient

mcp = FastMCP("fullenrich-server")
fullenrich = FullEnrichClient()


@mcp.tool()
async def enrich_contact(
    first_name: str,
    last_name: str,
    domain: str,
    linkedin_url: str = None,
) -> dict:
    """
    Get verified email and phone number for a B2B contact using FullEnrich's
    waterfall enrichment across 15+ data vendors.

    IMPORTANT: Only call this tool if the prospect's ICP score is >= 60.
    This tool consumes enrichment credits. Do not waste credits on unqualified leads.

    Args:
        first_name: Contact's first name
        last_name:  Contact's last name
        domain:     Company domain (e.g. rippling.com)
        linkedin_url: Optional LinkedIn profile URL for better match accuracy

    Returns:
        { "email": "...", "phone": "...", "confidence_score": 0-100 }
    """
    return await fullenrich.enrich(first_name, last_name, domain, linkedin_url)


@mcp.tool()
async def check_credits() -> dict:
    """
    Check remaining FullEnrich API credits.
    Call this if unsure whether credits are available before enriching a contact.

    Returns:
        { "credits_remaining": N, ... }
    """
    return await fullenrich.get_credits()


if __name__ == "__main__":
    mcp.run()
