from telebot.async_telebot import AsyncTeleBot
from .actual_send import toggle_actual_send
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_menu_markup():
    main_menu_markup = ReplyKeyboardMarkup(resize_keyboard=True)
    main_menu_markup.row(KeyboardButton("📊 Показать сигналы"), KeyboardButton("🔢 Количество сигналов"))
    main_menu_markup.row(KeyboardButton("▶️ Старт"), KeyboardButton("⏹ Стоп"))
    main_menu_markup.row(KeyboardButton("🔄 Переключить отправку"), KeyboardButton("❓ Помощь"))
    main_menu_markup.row(KeyboardButton("🗑 Удалить таблицы"), KeyboardButton("📋 Таблица сигналов"))
    main_menu_markup.row(KeyboardButton("⏱ Изменить интервал"), KeyboardButton("🔍 Проверить сейчас"))
    main_menu_markup.row(KeyboardButton("📁 Показать логи"), KeyboardButton("🗑 Удалить логи"))
    return main_menu_markup

async def show_signals_button(message, bot):
    from .show_signals import show_signals
    await show_signals(message, bot)

async def count_signals_button(message, bot):
    from .count_signals import count_signals
    await count_signals(message, bot)

async def start_bot_button(message, bot):
    from .start import start_bot
    await start_bot(message, bot)

async def stop_bot_button(message, bot):
    from .stop import stop_bot
    await stop_bot(message, bot)

async def actual_send_button(message, bot):
    await toggle_actual_send(message, bot)

async def help_button(message, bot):
    from .help import send_help
    await send_help(message, bot)

async def delete_tables_button(message, bot):
    from .delete_tables import delete_tables
    await delete_tables(message, bot)

async def table_signals_button(message, bot):
    from .table_signals import table_signals
    await table_signals(message, bot)

async def change_interval_button(message, bot):
    from .interval import change_interval
    await change_interval(message, bot)

async def check_command_button(message, bot):
    from .check import check_command
    await check_command(message, bot)

async def send_logs_button(message, bot):
    from .logs import send_logs
    await send_logs(message, bot)

async def delete_logs_button(message, bot):
    from .delete_logs import delete_logs
    await delete_logs(message, bot)