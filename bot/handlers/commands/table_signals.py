from telebot.async_telebot import AsyncTeleBot
from database.db_handler import fetch_all_signals
from utils.logger import general_logger
from utils.message_formatter import format_signals_table

async def table_signals(message, bot: AsyncTeleBot):
    general_logger.info("Запущена команда /table_signals.")
    signals = fetch_all_signals()
    if not signals:
        await bot.reply_to(message, "Таблица `signals` пуста.")
        general_logger.info("Таблица `signals` пуста.")
    else:
        table_message = format_signals_table(signals)
        await bot.reply_to(message, table_message)
        general_logger.info("Таблица `signals` отправлена.")