import logging
import asyncio
from telebot.async_telebot import AsyncTeleBot
from bot import setup_bot  # Корректный импорт setup_bot
from database.db_handler import init_db
from config import BOT_TOKEN
from bot.scheduler import start_scheduler

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s', handlers=[logging.StreamHandler()])

async def main():
    bot = AsyncTeleBot(BOT_TOKEN)

    while True:
        try:
            logging.info("Инициализация базы данных.")
            init_db()

            await setup_bot(bot)  # Вызов setup_bot для настройки бота
            logging.info("Бот настроен и готов к запуску.")

            await bot.infinity_polling()  # Запуск бота
        except Exception as e:
            logging.error(f"Произошла ошибка: {e}")
            logging.info("Перезапуск бота через 5 секунд...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    logging.info("Запуск приложения.")
    asyncio.run(main())