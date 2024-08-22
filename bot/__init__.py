import asyncio
from .handlers.commands import *
from bot.handlers.commands.menu_handlers import actual_send_button, get_main_menu_markup
from bot.handlers.commands.check import check_command
from bot.scheduler import start_scheduler
import logging

async def setup_bot(bot):
    logging.info("Настройка команд для бота началась")
    main_menu_markup = get_main_menu_markup()

    bot.message_handler(commands=['start'])(lambda message: asyncio.create_task(start_bot(message, bot)))
    bot.message_handler(commands=['stop'])(lambda message: asyncio.create_task(stop_bot(message, bot)))
    bot.message_handler(commands=['show'])(lambda message: asyncio.create_task(show_signals(message, bot)))
    bot.message_handler(commands=['count'])(lambda message: asyncio.create_task(count_signals(message, bot)))
    bot.message_handler(commands=['delete_tables'])(lambda message: asyncio.create_task(delete_tables(message, bot)))
    bot.message_handler(commands=['table_signals'])(lambda message: asyncio.create_task(table_signals(message, bot)))
    bot.message_handler(commands=['actual_send'])(lambda message: asyncio.create_task(toggle_actual_send(message, bot)))
    bot.message_handler(commands=['interval'])(lambda message: asyncio.create_task(change_interval(message, bot)))
    bot.message_handler(commands=['help'])(lambda message: asyncio.create_task(send_help(message, bot)))
    bot.message_handler(commands=['logs'])(lambda message: asyncio.create_task(send_logs(message, bot)))
    bot.message_handler(commands=['delete_logs'])(lambda message: asyncio.create_task(delete_logs(message, bot)))
    bot.message_handler(commands=['check'])(lambda message: asyncio.create_task(check_command(message, bot)))  # Регистрация команды /check

    logging.info("Команда /check зарегистрирована")

    @bot.message_handler(func=lambda message: True)
    async def send_welcome(message):
        await bot.reply_to(message, "Выберите команду:", reply_markup=main_menu_markup)

    return bot