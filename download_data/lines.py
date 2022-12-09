import asyncio
from repository import repo, models, session
from download_data import async_workers, async_queue
import utils


async def download_all_lines(bus_stop_list):
    await async_queue.concurrentry_process_tasks_chunks(
        tasks=bus_stop_list,
        async_task_fn=async_workers.handle_lines_for_id,
        concurrent_count=90,
        chunk_size=500,
        chunk_call=session.commit,
    )


if __name__ == "__main__":
    stop_registry = models.StopDataRegistry.from_queried_all(repo.get_bus_stops_sole())
    with utils.Timer():
        asyncio.get_event_loop().run_until_complete(
            download_all_lines(stop_registry.bus_stop_list)
        )
        # measured 5 - 7 minutes
