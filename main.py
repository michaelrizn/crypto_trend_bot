import logging
import asyncio
from telebot.async_telebot import AsyncTeleBot
from bot.handlers import setup_bot
from database.db_handler import init_db
from config import BOT_TOKEN
from bot.scheduler import start_scheduler

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s', handlers=[logging.StreamHandler()])

async def main():
    bot = AsyncTeleBot(BOT_TOKEN)  # Инициализация бота

    while True:
        try:
            # Инициализация базы данных
            logging.info("Инициализация базы данных.")
            init_db()

            # Настройка и запуск бота
            await setup_bot(bot)
            logging.info("Бот настроен и готов к запуску.")

            # Обработчик команды /start для получения chat_id и запуска планировщика
            @bot.message_handler(commands=['start'])
            async def start_command(message):
                chat_id = message.chat.id
                await bot.send_message(chat_id, "Планировщик запущен с интервалом 60 секунд.")
                await start_scheduler(60, bot, chat_id)  # Передаем chat_id в start_scheduler

            # Запуск бота
            await bot.infinity_polling()
        except Exception as e:
            logging.error(f"Произошла ошибка: {e}")
            logging.info("Перезапуск бота через 5 секунд...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    logging.info("Запуск приложения.")
    asyncio.run(main())