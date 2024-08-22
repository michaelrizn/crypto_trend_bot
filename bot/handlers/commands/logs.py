import logging
from pathlib import Path
from telebot.async_telebot import AsyncTeleBot
from utils.logger import general_logger

async def send_logs(message, bot: AsyncTeleBot):
    general_logger.info("Запрос логов через команду /logs")
    log_dir = Path(__file__).parents[4] / 'crypto_trend_bot' / 'logs'

    try:
        files = list(log_dir.iterdir())  # Получаем все файлы в директории
        if not files:
            await bot.send_message(message.chat.id, "Нет доступных файлов для отправки.")
            general_logger.info("Нет доступных файлов для отправки.")
            return

        for log_file in files:
            if log_file.is_file():  # Проверяем, что это файл, а не директория
                if log_file.stat().st_size == 0:
                    logging.info(f"Файл {log_file.name} пустой, пропускаем его отправку.")
                    await bot.send_message(message.chat.id,
                                           f"Файл {log_file.name} пустой и не будет отправлен.")
                    continue

                with open(log_file, 'rb') as file:
                    await bot.send_document(message.chat.id, file, caption=f"Файл: {log_file.name}")
                    general_logger.info(f"Файл {log_file.name} отправлен.")

    except Exception as e:
        general_logger.error(f"Ошибка при отправке файлов: {e}")
        await bot.send_message(message.chat.id, "Произошла ошибка при отправке файлов.")