from apscheduler.schedulers.asyncio import AsyncIOScheduler
import logging
import asyncio

scheduler = AsyncIOScheduler()

async def start_scheduler(job_func, chat_id):
    logging.info("Инициализация и запуск планировщика.")
    scheduler.add_job(lambda: asyncio.create_task(job_func(chat_id)), 'interval', seconds=60)
    scheduler.start()
    logging.info("Планировщик запущен.")
    return scheduler

def update_scheduler_interval(new_interval, job_func, chat_id):
    global scheduler
    logging.info(f"Обновление интервала планировщика на {new_interval} секунд.")
    scheduler.remove_all_jobs()
    scheduler.add_job(lambda: asyncio.create_task(job_func(chat_id)), 'interval', seconds=new_interval)
    logging.info(f"Интервал планировщика обновлен на {new_interval} секунд.")

def stop_scheduler():
    global scheduler
    if scheduler.running:
        scheduler.shutdown()
        logging.info("Планировщик остановлен.")