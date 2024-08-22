from telebot.async_telebot import AsyncTeleBot
from database.db_handler import get_signals_count
from utils.logger import general_logger

async def count_signals(message, bot: AsyncTeleBot):
    general_logger.info("Запущена команда /count.")
    active_count, closed_count = get_signals_count()
    await bot.reply_to(
        message,
        f"Количество открытых сигналов: {active_count}\nКоличество закрытых сигналов: {closed_count}"
    )
    general_logger.info(
        f"Количество открытых сигналов: {active_count}, закрытых сигналов: {closed_count}"
    )