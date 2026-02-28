import asyncio
from backend.agent.researcher import run_research_agent
from backend.utils.logger import get_logger
import logging
import sys

logger = get_logger(__name__)

# ensure we get all logs
logging.getLogger().setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)

prospect = {
    "first_name": "Alex",
    "last_name": "Rivera",
    "company": "Rippling",
    "title": "Head of Growth",
    "domain": "rippling.com"
}

async def main():
    print("STARTING TEST")
    try:
        res = await run_research_agent(prospect)
        print("FINAL RESULT:", res)
    except Exception as e:
        print("ERROR:", str(e))

asyncio.run(main())
