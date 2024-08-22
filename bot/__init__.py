import asyncio
from .handlers.commands import *
from bot.handlers.commands.menu_handlers import actual_send_button, get_main_menu_markup
from bot.handlers.commands.check import check_command
from bot.scheduler import start_scheduler
import logging

async def setup_bot(bot):
    logging.info("Настройка команд для бота")

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
    bot.message_handler(commands=['check'])(lambda message: asyncio.create_task(check_command(message, bot)))  # Добавляем команду /check

    logging.info("Команда /check зарегистрирована")

    # Обработчик команды /start
    @bot.message_handler(commands=['start'])
    async def start_command(message):
        chat_id = message.chat.id
        await bot.send_message(chat_id, "Планировщик запущен с интервалом 60 секунд.")
        await start_scheduler(60, bot, chat_id)

    bot.message_handler(func=lambda message: message.text == "📊 Показать сигналы")(lambda message: asyncio.create_task(show_signals_button(message, bot)))
    bot.message_handler(func=lambda message: message.text == "🔢 Количество сигналов")(lambda message: asyncio.create_task(count_signals_button(message, bot)))
    bot.message_handler(func=lambda message: message.text == "▶️ Старт")(lambda message: asyncio.create_task(start_bot_button(message, bot)))
    bot.message_handler(func=lambda message: message.text == "⏹ Стоп")(lambda message: asyncio.create_task(stop_bot_button(message, bot)))
    bot.message_handler(func=lambda message: message.text == "Актуальная отправка")(lambda message: asyncio.create_task(actual_send_button(message, bot)))
    bot.message_handler(func=lambda message: message.text == "❓ Помощь")(lambda message: asyncio.create_task(help_button(message, bot)))

    @bot.message_handler(func=lambda message: True)
    async def send_welcome(message):
        await bot.reply_to(message, "Выберите команду:", reply_markup=main_menu_markup)

    return bot