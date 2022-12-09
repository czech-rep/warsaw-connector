import asyncio
from more_itertools import chunked
from typing import List


"""based on https://docs.python.org/3.9/library/asyncio-queue.html"""


async def worker(queue: asyncio.Queue, async_work_fn, tm=30):
    while True:
        task = queue.get_nowait()
        try:
            await asyncio.wait_for(async_work_fn(task), timeout=tm)
        except asyncio.TimeoutError:
            print(f"timeout on {task}")
            queue.put_nowait(task)
        queue.task_done()


async def concurrentry_process_tasks(tasks: List, async_task_fn, concurrent_count=50):
    queue = asyncio.Queue()
    for task in tasks:
        queue.put_nowait(task)
    tasks = [asyncio.create_task(worker(queue, async_task_fn)) for _ in range(concurrent_count)]
    print("queue starts")
    await queue.join()
    print("all joined")

    for task in tasks:
        task.cancel()
    # Wait until all worker tasks are cancelled.
    await asyncio.gather(*tasks, return_exceptions=True)

    print("end all")


async def concurrentry_process_tasks_chunks(
    tasks: List, async_task_fn, concurrent_count=50, chunk_size=1000, chunk_call=lambda: None
):
    """after every chunk, call chunk_call callable"""
    for idx, chunk in enumerate(chunked(tasks, chunk_size)):
        queue = asyncio.Queue()
        for task in chunk:
            queue.put_nowait(task)
        tasks = [asyncio.create_task(worker(queue, async_task_fn)) for _ in range(concurrent_count)]
        print("queue starts")
        await queue.join()
        print("all joined")

        for task in tasks:
            task.cancel()
        # Wait until all worker tasks are cancelled.
        await asyncio.gather(*tasks, return_exceptions=True)

        chunk_call()
        print("end chunk", idx)
    print("end all")
