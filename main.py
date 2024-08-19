import logging
import asyncio
from bot.handlers import setup_bot
from database.db_handler import init_db

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s', handlers=[logging.StreamHandler()])

async def main():
    while True:
        try:
            # Инициализация базы данных
            logging.info("Инициализация базы данных.")
            init_db()

            # Настройка и запуск бота
            bot = await setup_bot()
            logging.info("Бот настроен и готов к запуску.")

            # Запуск бота
            await bot.infinity_polling()
        except Exception as e:
            logging.error(f"Произошла ошибка: {e}")
            logging.info("Перезапуск бота через 5 секунд...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    logging.info("Запуск приложения.")
    asyncio.run(main())