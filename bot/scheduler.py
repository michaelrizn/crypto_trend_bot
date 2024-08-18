from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import CHECK_INTERVAL
import logging
import asyncio

async def start_scheduler(job_func, chat_id):
    logging.info("Инициализация и запуск планировщика.")
    scheduler = AsyncIOScheduler()
    scheduler.add_job(lambda: asyncio.create_task(job_func(chat_id)), 'interval', seconds=CHECK_INTERVAL)
    scheduler.start()
    logging.info(f"Планировщик запущен с интервалом {CHECK_INTERVAL} секунд.")
    return scheduler

def stop_scheduler(scheduler):
    if scheduler.running:
        scheduler.shutdown()
        logging.info("Планировщик остановлен.")