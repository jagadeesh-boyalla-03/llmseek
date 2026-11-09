import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import asyncio
import httpx
from backend.main import app

async def run():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        res = await client.get("/")
        print("Root response:", res.status_code, res.json())

if __name__ == "__main__":
    asyncio.run(run())
