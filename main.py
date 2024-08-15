import asyncio
from bot.handlers import setup_bot
from database.db_handler import init_db

async def main():
    # Инициализация базы данных
    init_db()

    # Настройка и запуск бота
    bot = await setup_bot()

    # Запуск бота
    await bot.infinity_polling()

if __name__ == "__main__":
    asyncio.run(main())