# Zyga — Research & Enrichment Agent PoC

AI-powered B2B prospect research and enrichment agent. Uses **GPT-5** (via GitHub Models) with **MCP architecture** to autonomously research, qualify, and enrich prospects.

## Architecture

```
Web UI (HTML/CSS/JS)  →  FastAPI Backend  →  Research Agent (GPT-5 + mcp-use)
                                                  ├── Linkup MCP (web search)
                                                  └── FullEnrich MCP (contact enrichment)
```

## Quick Start

### 1. Prerequisites

- Python 3.10+
- [GitHub Personal Access Token](https://github.com/settings/tokens) (for GPT-5 via GitHub Models — free)
- [Linkup API Key](https://linkup.so) (free tier — €5/month credit)
- [FullEnrich API Key](https://fullenrich.com) (free trial credits)

### 2. Install

```bash
cd zyga-research-poc
pip install -r requirements.txt
```

### 3. Configure

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```bash
GITHUB_TOKEN=ghp_your_github_pat_here
LINKUP_API_KEY=lp_your_linkup_key_here
FULLENRICH_API_KEY=fe_your_fullenrich_key_here
```

### 4. Run

```bash
uvicorn backend.main:app --reload --port 8000
```

Open **http://localhost:8000** in your browser.

## Demo Scenarios

Three pre-built scenarios showcase the agent's intelligence:

| Scenario | Prospect | Expected ICP | Enrichment? |
|---|---|---|---|
| **High ICP** | Alex Rivera, Head of Growth @ Rippling | ~85 | ✅ Yes |
| **Medium ICP** | Marie Dupont, Marketing Director @ Pennylane | ~68 | ✅ Yes |
| **Low ICP** | David Martin, Freelance Consultant | ~15 | ❌ No (credits saved) |

## Key Features

- **Autonomous research**: GPT-5 decides which tools to call and in what order
- **Credit-gating**: Enrichment only triggered when ICP score ≥ 60 (rule in tool description, not hardcoded)
- **MCP architecture**: Add new data sources without touching agent code
- **Agent trace panel**: Visual timeline of every tool call for demo presentations

## Project Structure

```
zyga-research-poc/
├── backend/
│   ├── main.py              # FastAPI entry point
│   ├── config.py             # Environment config
│   ├── agent/                # Research agent (GPT-5 + mcp-use)
│   ├── api/                  # API routes & models
│   ├── mcp_servers/          # Custom MCP servers
│   │   └── fullenrich/       # FullEnrich MCP wrapper
│   └── utils/                # Logging
├── frontend/                 # HTML + CSS + JS
├── demo/                     # Sample prospects & expected outputs
├── .env.example              # Environment template
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Tech Stack

| Layer | Technology |
|---|---|
| LLM | GPT-5 via GitHub Models (free) |
| Agent | mcp-use + LangChain |
| Search | Linkup (official MCP server) |
| Enrichment | FullEnrich (custom FastMCP server) |
| Backend | FastAPI |
| Frontend | Vanilla HTML/CSS/JS |
