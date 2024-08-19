import logging
from services.signal_manager import check_and_create_signals, update_active_signals
from database.db_handler import move_old_signals_to_history, get_active_signals, get_closed_signals, mark_signal_as_reported
from config import CRYPTO_PAIRS, TIMEZONE
from utils.message_formatter import format_new_signal_message, format_closed_signal_message
from datetime import datetime
from pytz import timezone
from telebot.async_telebot import AsyncTeleBot
from config import BOT_TOKEN
from .utils import send_signal_messages

bot = AsyncTeleBot(BOT_TOKEN)

async def perform_check(chat_id=None):
    try:
        logging.info("Начало выполнения perform_check().")
        check_and_create_signals(CRYPTO_PAIRS)
        update_active_signals()

        if chat_id:
            current_time = datetime.now(timezone(TIMEZONE)).strftime("%Y-%m-%d %H:%M")
            separator = "-" * 40
            await bot.send_message(chat_id, f"{current_time}\n{separator}")

            active_signals = get_active_signals()
            logging.info(f"Получено {len(active_signals)} активных сигналов.")
            await send_signal_messages(bot, chat_id, active_signals, format_new_signal_message)

            closed_signals = get_closed_signals()
            if closed_signals:
                logging.info(f"Получено {len(closed_signals)} закрытых сигналов.")
                await send_signal_messages(bot, chat_id, closed_signals, format_closed_signal_message)
                for signal in closed_signals:
                    mark_signal_as_reported(signal[0])
                logging.info("Обработаны закрытые сигналы.")

        move_old_signals_to_history()
        logging.info("Завершено выполнение perform_check().")
    except Exception as e:
        logging.error(f"Ошибка при выполнении perform_check: {e}")