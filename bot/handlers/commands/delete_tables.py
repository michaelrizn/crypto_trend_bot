from telebot.async_telebot import AsyncTeleBot
from database.db_handler import delete_all_tables, init_db
from utils.logger import general_logger

async def delete_tables(message, bot: AsyncTeleBot):
    general_logger.info("Command /delete_tables initiated.")
    delete_all_tables()
    init_db()
    await bot.reply_to(message, "All tables have been deleted and recreated.")
    general_logger.info("All tables deleted and recreated.")