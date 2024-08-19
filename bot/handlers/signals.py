import logging
from telebot.async_telebot import AsyncTeleBot
from database.db_handler import get_active_signals, get_closed_signals, mark_signal_as_reported, get_signals_count
from utils.message_formatter import format_new_signal_message, format_closed_signal_message
from config import BOT_TOKEN
from .utils import send_signal_messages

bot = AsyncTeleBot(BOT_TOKEN)

@bot.message_handler(commands=['show'])
async def show_signals(message):
    logging.info("Запущена команда /show.")
    active_signals = get_active_signals()
    if not active_signals:
        logging.info("Нет активных сигналов.")
        await bot.reply_to(message, "В данный момент нет активных сигналов.")
    else:
        logging.info(f"Отображение {len(active_signals)} активных сигналов.")
        await send_signal_messages(bot, message.chat.id, active_signals, format_new_signal_message)

    closed_signals = get_closed_signals()
    if closed_signals:
        logging.info(f"Отображение {len(closed_signals)} закрытых сигналов.")
        await send_signal_messages(bot, message.chat.id, closed_signals, format_closed_signal_message)
        for signal in closed_signals:
            mark_signal_as_reported(signal[0])
        logging.info("Закрытые сигналы обработаны и отмечены как отправленные.")
    else:
        logging.info("Нет закрытых сигналов.")
        await bot.reply_to(message, "В данный момент нет закрытых сигналов.")

@bot.message_handler(commands=['count'])
async def count_signals(message):
    logging.info("Запущена команда /count.")
    active_count, closed_count = get_signals_count()
    logging.info(f"Количество открытых сигналов: {active_count}, закрытых сигналов: {closed_count}")
    await bot.reply_to(message, f"Количество открытых сигналов: {active_count}\nКоличество закрытых сигналов: {closed_count}")