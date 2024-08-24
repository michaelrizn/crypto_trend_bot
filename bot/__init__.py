import asyncio
import logging
import traceback
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
    send_logs_button, delete_logs_button, actual_send_button
)
from bot.handlers.commands.check import check_command

async def setup_bot(bot):
    logging.info("Настройка команд для бота началась")
    main_menu_markup = get_main_menu_markup()

    def log_and_execute(func):
        async def wrapper(message):
            try:
                logging.info(f"Выполнение команды: {func.__name__}")
                await func(message, bot)
            except Exception as e:
                logging.error(f"Ошибка при выполнении {func.__name__}: {e}")
                logging.error(f"Traceback: {traceback.format_exc()}")
        return wrapper

    # Регистрация текстовых команд
    command_handlers = [
        ('start', start_bot),
        ('scheduler_start', start_scheduler_command),
        ('stop', stop_bot),
        ('show', show_signals),
        ('count', count_signals),
        ('delete_tables', delete_tables),
        ('table_signals', table_signals),
        ('actual_send', toggle_actual_send),
        ('interval', change_interval),
        ('help', send_help),
        ('logs', send_logs),
        ('delete_logs', delete_logs),
        ('check', check_command),
        ('send_signals', send_pending_signals)
    ]

    for command, handler in command_handlers:
        bot.register_message_handler(log_and_execute(handler), commands=[command])

    # Регистрация кнопок меню
    button_handlers = [
        ("📊 Показать сигналы", show_signals_button),
        ("🔢 Количество сигналов", count_signals_button),
        ("▶️ Старт", start_bot_button),
        ("⏹ Стоп", stop_bot_button),
        ("❓ Помощь", help_button),
        ("🗑 Удалить таблицы", delete_tables_button),
        ("📋 Таблица сигналов", table_signals_button),
        ("⏱ Изменить интервал", change_interval_button),
        ("🔍 Проверить сейчас", check_command_button),
        ("📁 Показать логи", send_logs_button),
        ("🗑 Удалить логи", delete_logs_button),
        ("🔄 Переключить отправку", actual_send_button)
    ]

    for button_text, handler in button_handlers:
        bot.register_message_handler(log_and_execute(handler), func=lambda message, text=button_text: message.text == text)

    # Обработчик по умолчанию для сообщений без команд
    async def send_welcome(message):
        logging.info("Выполнение обработчика по умолчанию")
        await bot.reply_to(message, "Выберите команду:", reply_markup=main_menu_markup)

    bot.register_message_handler(send_welcome, func=lambda message: True)

    logging.info("Настройка команд для бота завершена")
    return bot