from telebot.async_telebot import AsyncTeleBot
from utils.logger import general_logger
from services.signal_manager import check_and_create_signals
from config import CRYPTO_PAIRS
from bot.handlers.commands.show_signals import send_pending_signals
import logging


async def check_command(message, bot: AsyncTeleBot):
    logging.info("Команда /check вызвана")
    general_logger.info("Запущена команда /check")
    chat_id = message.chat.id
    await bot.send_message(chat_id, "Начинаю внеплановую проверку сигналов...")

    new_signals, updated_signals, closed_signals = await check_and_create_signals(CRYPTO_PAIRS)

    general_logger.info(
        f"Новых сигналов: {len(new_signals)}, обновленных: {len(updated_signals)}, закрытых: {len(closed_signals)}")

    await send_pending_signals(bot, chat_id)

    await bot.send_message(chat_id, "Внеплановая проверка сигналов завершена.")
    general_logger.info("Внеплановая проверка сигналов завершена")