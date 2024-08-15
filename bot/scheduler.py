from apscheduler.schedulers.asyncio import AsyncIOScheduler

async def start_scheduler(job_func):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(job_func, 'interval', hours=1)  # Запуск каждый час
    scheduler.start()
    return scheduler

def stop_scheduler(scheduler):
    if scheduler.running:
        scheduler.shutdown()