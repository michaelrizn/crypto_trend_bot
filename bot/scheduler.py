import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from services.signal_manager import check_and_create_signals
from bot.handlers.commands.show_signals import send_pending_signals
from database.db_handler import store_signals_for_sending
from config import CRYPTO_PAIRS  # Импортируем список криптовалютных пар

scheduler = AsyncIOScheduler()
job = None
current_interval = None
user_chat_id = None  # Глобальная переменная для хранения chat_id

async def start_scheduler(check_interval, bot, chat_id):
    global job, current_interval, scheduler, user_chat_id
    logging.info("Инициализация и запуск планировщика.")

    user_chat_id = chat_id  # Сохраняем chat_id пользователя

    if scheduler.running:
        scheduler.shutdown()

    scheduler = AsyncIOScheduler()
    current_interval = check_interval
    job = scheduler.add_job(
        process_signals_func,
        trigger=IntervalTrigger(seconds=check_interval),
        args=[bot],
        id='process_signals'
    )
    scheduler.start()
    logging.info(f"Планировщик запущен с интервалом {check_interval} секунд.")

def stop_scheduler():
    global job, current_interval, scheduler
    if scheduler.running:
        scheduler.shutdown()
        job = None
        current_interval = None
        logging.info("Планировщик остановлен.")
    else:
        logging.info("Планировщик уже остановлен.")

def get_current_interval():
    global current_interval
    return current_interval

def update_scheduler_interval(new_interval):
    global job, current_interval, scheduler
    if scheduler.running and job:
        scheduler.reschedule_job(
            'process_signals', trigger=IntervalTrigger(seconds=new_interval)
        )
        current_interval = new_interval
        logging.info(f"Интервал работы планировщика обновлен до {new_interval} секунд.")
    else:
        logging.warning("Планировщик не запущен, обновление интервала невозможно.")

async def process_signals_func(bot):
    global user_chat_id
    logging.info("Начало выполнения периодической проверки сигналов.")
    try:
        chat_id = user_chat_id  # Используем сохраненный chat_id
        if chat_id is None:
            logging.error("Chat ID пользователя не установлен.")
            return

        # Вызов функции с передачей CRYPTO_PAIRS
        new_signals, updated_signals, closed_signals = await check_and_create_signals(CRYPTO_PAIRS)

        logging.info(
            f"Получено новых сигналов: {len(new_signals)}, обновленных: {len(updated_signals)}, закрытых: {len(closed_signals)}"
        )

        # Сохраняем сигналы для отправки
        store_signals_for_sending(new_signals, updated_signals, closed_signals)

        # Отправляем сохраненные сигналы
        await send_pending_signals(bot, chat_id)

        logging.info("Периодическая проверка сигналов завершена успешно.")
    except Exception as e:
        logging.error(f"Ошибка при выполнении периодической проверки сигналов: {e}")
        import traceback
        logging.error(traceback.format_exc())