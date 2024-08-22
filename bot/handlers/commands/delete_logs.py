import os
from pathlib import Path
from telebot.async_telebot import AsyncTeleBot
from utils.logger import general_logger, setup_logging

async def delete_logs(message, bot: AsyncTeleBot):
    general_logger.info("Запущена команда /delete_logs")
    try:
        log_dir = Path(__file__).parents[3] / 'logs'
        deleted_files = 0
        for file in os.listdir(log_dir):
            if file.endswith(".log"):
                os.remove(os.path.join(log_dir, file))
                deleted_files += 1

        # Создаем новые пустые файлы логов
        open(log_dir / 'general.log', 'w').close()
        open(log_dir / 'analyze.log', 'w').close()

        # Переинициализируем логгеры
        new_general_logger, new_analyze_logger = setup_logging()

        # Обновляем глобальные переменные в модуле utils.logger
        import utils.logger
        utils.logger.general_logger = new_general_logger
        utils.logger.analyze_logger = new_analyze_logger

        response = f"Удалено файлов логов: {deleted_files}. Созданы новые пустые файлы логов."
        await bot.reply_to(message, response)
        new_general_logger.info(
            f"Удалено {deleted_files} файлов логов. Созданы новые пустые файлы.")
    except Exception as e:
        general_logger.error(f"Ошибка при удалении логов: {e}")
        response = "Произошла ошибка при удалении логов."
        await bot.reply_to(message, response)