# MCP Servers — Zyga Research & Enrichment PoC

## Architecture

This PoC connects the Research Agent to external tools via **MCP (Model Context Protocol)**:

| Server | Type | Description |
|---|---|---|
| **Linkup** | Remote (official) | Real-time web search, `standard` and `deep` modes |
| **FullEnrich** | Local (custom) | Contact enrichment via waterfall across 15+ vendors |

## Linkup

- **URL**: `https://mcp.linkup.so/mcp?apiKey=YOUR_KEY`
- Off-the-shelf, no custom code needed
- Tools exposed: `linkup_search`, `linkup_fetch`

## FullEnrich (Custom)

- Built with **FastMCP** (`backend/mcp_servers/fullenrich/server.py`)
- Wraps the FullEnrich REST API (`client.py`)
- Tools: `enrich_contact`, `check_credits`
- **Credit-gating rule** is in the `enrich_contact` tool description — the LLM reads it and decides when to use the tool

### Running Standalone

```bash
python -m backend.mcp_servers.fullenrich.server
```

In normal operation, `mcp-use` launches this server automatically as a subprocess.
