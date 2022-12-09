import sys
import asyncio
from repository import repo, models, session
from download_data import async_workers, async_queue
import utils
from typing import List


async def download_time_tables(bus_stops: List):
    await async_queue.concurrentry_process_tasks_chunks(
        tasks=bus_stops,
        async_task_fn=async_workers.handle_timetables_for_one_stop,
        concurrent_count=70, # at 100 workers works bad due to timeouts (api is too slow?)
        chunk_size=400,
        chunk_call=session.commit,
    )


if __name__ == "__main__":
    """we download time tables by bus stops
    here u can restrict bus stop ids
    """
    if len(sys.argv) > 1:
        from_id = int(sys.argv[1])
        limit = int(sys.argv[2])
    else:
        from_id, limit = 0, None

    stop_registry = models.StopDataRegistry.from_queried_all(repo.get_bus_stops_from(from_id, limit))
    with utils.Timer():
        asyncio.get_event_loop().run_until_complete(
            download_time_tables(stop_registry.bus_stop_list)
        )
    # around 15 minutes
