import asyncio
import time

import aiohttp

URL = "http://localhost:8001/api/v1/dummy/"

CONCURRENCY = 500
REQUESTS = 20000


async def worker(session):
    async with session.get(URL) as r:
        await r.text()

    async with session.post(URL, json={"name": "test"}) as r:
        await r.text()


async def main():
    start = time.time()

    async with aiohttp.ClientSession() as session:
        tasks = [
            asyncio.create_task(worker(session))
            for _ in range(REQUESTS)
        ]

        await asyncio.gather(*tasks)

    print(f"Done in {time.time() - start:.2f}s")


asyncio.run(main())
