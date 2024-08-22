from telebot.async_telebot import AsyncTeleBot
from utils.logger import general_logger
from bot.scheduler import process_signals_func
import logging

async def check_command(message, bot: AsyncTeleBot):
    logging.info("Команда /check вызвана")
    general_logger.info("Запущена команда /check")
    chat_id = message.chat.id
    await bot.send_message(chat_id, "Начинаю внеплановую проверку сигналов...")

    await process_signals_func(bot)

    await bot.send_message(chat_id, "Внеплановая проверка сигналов завершена.")
    general_logger.info("Внеплановая проверка сигналов завершена")