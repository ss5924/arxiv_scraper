import asyncio
import random
from asyncio import Semaphore
from aiohttp import ClientSession
from database import async_session
from tasks import load_pending_tasks, mark_task_done, mark_task_failed
from fetcher import fetch_papers
from config import RATE_LIMIT_DELAY, TASK_POLL_INTERVAL, SEMAPHORE_LIMIT, WORKER_COUNT, setup_logger
import logging


async def worker(worker_id: int, queue, session_factory, semaphore: Semaphore):
    async with ClientSession() as http_session:
        while not queue.empty():
            task = await queue.get()
            logging.info(f"[worker {worker_id}] task started: {task}")
            try:
                async with session_factory() as db_session:
                    success = await fetch_papers(http_session, task, db_session, semaphore)
                    if success:
                        await mark_task_done(db_session, task["id"])
                    else:
                        await mark_task_failed(db_session, task["id"])
                await asyncio.sleep(random.uniform(*RATE_LIMIT_DELAY))
            finally:
                logging.info(f"[worker {worker_id}] task finished: {task}")
                queue.task_done()


async def main_loop(worker_count: int):
    semaphore = Semaphore(SEMAPHORE_LIMIT)

    while True:
        async with async_session() as session:
            tasks = await load_pending_tasks(session)

        if tasks:
            queue = asyncio.Queue()
            for task in tasks:
                queue.put_nowait(task)

            workers = [
                asyncio.create_task(worker(i, queue, async_session, semaphore))
                for i in range(worker_count)
            ]
            await queue.join()

            for w in workers:
                w.cancel()

        await asyncio.sleep(TASK_POLL_INTERVAL)


if __name__ == "__main__":
    setup_logger()
    asyncio.run(main_loop(WORKER_COUNT))
