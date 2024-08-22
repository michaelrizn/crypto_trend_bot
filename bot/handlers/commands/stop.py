import asyncio
from telebot.async_telebot import AsyncTeleBot
from utils.logger import general_logger
from bot.scheduler import stop_scheduler

check_task = None

async def stop_bot(message, bot: AsyncTeleBot):
    global check_task
    if check_task and not check_task.done():
        check_task.cancel()
        try:
            await check_task
        except asyncio.CancelledError:
            pass
        check_task = None
        stop_scheduler()  # Останавливаем планировщик
        general_logger.info("Бот остановлен. Периодические проверки деактивированы.")
        response = "Бот остановлен. Периодические проверки деактивированы."
        await bot.reply_to(message, response)
    else:
        general_logger.info("Бот не запущен.")
        response = "Бот не запущен."
        await bot.reply_to(message, response)