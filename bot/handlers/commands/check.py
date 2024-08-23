from telebot.async_telebot import AsyncTeleBot
from utils.logger import general_logger
from services.signal_manager import check_and_create_signals
from bot.handlers.commands.show_signals import show_signals  # Импорт функции show_signals
from config import CRYPTO_PAIRS  # Импорт списка криптовалютных пар из config.py

async def check_command(message, bot: AsyncTeleBot):
    general_logger.info("Команда /check вызвана")
    await bot.reply_to(message, "Начинаю внеплановую проверку сигналов...")

    # Передаем CRYPTO_PAIRS в функцию check_and_create_signals
    await check_and_create_signals(CRYPTO_PAIRS)

    general_logger.info("Внеплановая проверка сигналов завершена.")
    await bot.reply_to(message, "Внеплановая проверка сигналов завершена.")

    # Вызов функции show_signals после завершения проверки
    await show_signals(message, bot)
    general_logger.info("Автоматическая отправка сигналов после проверки завершена.")