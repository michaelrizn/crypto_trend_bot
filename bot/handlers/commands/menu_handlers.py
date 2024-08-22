from telebot.async_telebot import AsyncTeleBot
from .actual_send import toggle_actual_send
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_menu_markup():
    main_menu_markup = ReplyKeyboardMarkup(resize_keyboard=True)
    main_menu_markup.row(KeyboardButton("📊 Показать сигналы"), KeyboardButton("🔢 Количество сигналов"))
    main_menu_markup.row(KeyboardButton("▶️ Старт"), KeyboardButton("⏹ Стоп"))
    main_menu_markup.row(KeyboardButton("/actual_send"), KeyboardButton("❓ Помощь"))
    main_menu_markup.row(KeyboardButton("/delete_tables"), KeyboardButton("/table_signals"))
    main_menu_markup.row(KeyboardButton("/interval"), KeyboardButton("/check"))
    main_menu_markup.row(KeyboardButton("/logs"), KeyboardButton("/delete_logs"))
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