import asyncio
from bot.handlers.commands import (
    start_bot, start_scheduler_command, stop_bot, show_signals,
    count_signals, delete_tables, table_signals, toggle_actual_send,
    change_interval, send_help, send_logs, delete_logs, send_pending_signals
)
from bot.handlers.commands.menu_handlers import (
    get_main_menu_markup, show_signals_button, count_signals_button,
    start_bot_button, stop_bot_button, help_button,
    delete_tables_button, table_signals_button,
    change_interval_button, check_command_button,
    send_logs_button, delete_logs_button
)
from bot.handlers.commands.check import check_command
import logging

async def setup_bot(bot):
    logging.info("Настройка команд для бота началась")
    main_menu_markup = get_main_menu_markup()

    # Регистрация текстовых команд
    bot.message_handler(commands=['start'])(lambda message: asyncio.create_task(start_bot(message, bot)))
    bot.message_handler(commands=['scheduler_start'])(lambda message: asyncio.create_task(start_scheduler_command(message, bot)))
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
    bot.message_handler(commands=['check'])(lambda message: asyncio.create_task(check_command(message, bot)))
    bot.message_handler(commands=['send_signals'])(lambda message: asyncio.create_task(send_pending_signals(message, bot)))

    # Регистрация кнопок меню
    bot.message_handler(func=lambda message: message.text == "📊 Показать сигналы")(lambda message: show_signals_button(message, bot))
    bot.message_handler(func=lambda message: message.text == "🔢 Количество сигналов")(lambda message: count_signals_button(message, bot))
    bot.message_handler(func=lambda message: message.text == "▶️ Старт")(lambda message: start_bot_button(message, bot))
    bot.message_handler(func=lambda message: message.text == "⏹ Стоп")(lambda message: stop_bot_button(message, bot))
    bot.message_handler(func=lambda message: message.text == "❓ Помощь")(lambda message: help_button(message, bot))
    bot.message_handler(func=lambda message: message.text == "🗑 Удалить таблицы")(lambda message: delete_tables_button(message, bot))
    bot.message_handler(func=lambda message: message.text == "📋 Таблица сигналов")(lambda message: table_signals_button(message, bot))
    bot.message_handler(func=lambda message: message.text == "⏱ Изменить интервал")(lambda message: change_interval_button(message, bot))
    bot.message_handler(func=lambda message: message.text == "🔍 Проверить сейчас")(lambda message: check_command_button(message, bot))
    bot.message_handler(func=lambda message: message.text == "📁 Показать логи")(lambda message: send_logs_button(message, bot))
    bot.message_handler(func=lambda message: message.text == "🗑 Удалить логи")(lambda message: delete_logs_button(message, bot))

    # Обработчик по умолчанию для сообщений без команд
    @bot.message_handler(func=lambda message: True)
    async def send_welcome(message):
        await bot.reply_to(message, "Выберите команду:", reply_markup=main_menu_markup)

    return bot