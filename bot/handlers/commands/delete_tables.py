from telebot.async_telebot import AsyncTeleBot
from database.db_handler import delete_all_tables, init_db
from utils.logger import general_logger

async def delete_tables(message, bot: AsyncTeleBot):
    general_logger.info("Запущена команда /delete_tables.")
    delete_all_tables()
    init_db()
    await bot.reply_to(message, "Все таблицы были удалены и заново созданы.")
    general_logger.info("Все таблицы удалены и заново созданы.")