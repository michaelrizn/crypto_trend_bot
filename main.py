import logging
import asyncio
from telebot.async_telebot import AsyncTeleBot
from bot import setup_bot
from database.db_handler import init_db
from config import BOT_TOKEN
from bot.scheduler import start_scheduler

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s',
                    handlers=[logging.StreamHandler()])

# Отключаем логи для библиотек
logging.getLogger("asyncio").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("ccxt").setLevel(logging.WARNING)

async def main():
    bot = AsyncTeleBot(BOT_TOKEN)
    logging.info(f"Тип переменной bot: {type(bot)}")

    while True:
        try:
            logging.info("Инициализация базы данных.")
            init_db()

            logging.info("Настройка бота.")
            await setup_bot(bot)
            logging.info("Бот настроен и готов к запуску.")
            logging.info(f"Тип переменной bot перед infinity_polling: {type(bot)}")

            logging.info("Запуск infinity_polling.")
            await bot.infinity_polling(timeout=10, request_timeout=15)

        except Exception as e:
            logging.error(f"Произошла ошибка: {e}")
            logging.info("Перезапуск бота через 5 секунд...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    logging.info("Запуск приложения.")
    asyncio.run(main())