from telebot.async_telebot import AsyncTeleBot
from database.db_handler import (
    get_active_signals,
    get_closed_signals,
    mark_signal_as_reported,
    get_signals_to_send,
    mark_signal_as_sent,
    get_signal_by_id,
    increment_count_sends
)
from utils.logger import general_logger
from utils.message_formatter import format_new_signal_message, format_closed_signal_message, \
    add_timestamp_and_separator
from bot.handlers.utils import send_signal_messages
from config import get_actual_signals_status

async def show_signals(message, bot: AsyncTeleBot):
    general_logger.info("Command /show initiated.")
    chat_id = message.chat.id

    active_signals = get_active_signals()
    if not active_signals:
        general_logger.info("No active signals.")
        await bot.reply_to(message, "There are no active signals at the moment.")
    else:
        general_logger.info(f"Found {len(active_signals)} active signals.")
        await send_signal_messages(
            chat_id=chat_id, signals=active_signals, format_message_func=format_new_signal_message
        )

    closed_signals = get_closed_signals()
    if closed_signals:
        general_logger.info(f"Found {len(closed_signals)} closed signals.")
        await send_signal_messages(
            chat_id=chat_id,
            signals=closed_signals,
            format_message_func=format_closed_signal_message
        )
        for signal in closed_signals:
            mark_signal_as_reported(signal.id)
        general_logger.info("Closed signals processed and marked as reported.")
    else:
        general_logger.info("No closed signals.")
        await bot.reply_to(message, "There are no closed signals at the moment.")

async def send_pending_signals(bot: AsyncTeleBot, chat_id):
    general_logger.info("Processing pending signals.")
    signals_to_send = get_signals_to_send()
    send_actual = get_actual_signals_status()

    signals_dict = {}
    for signal_id, signal_type in signals_to_send:
        signal = get_signal_by_id(signal_id)
        if signal:
            signals_dict[signal_id] = signal

    general_logger.info(f"Using chat_id: {chat_id}")

    if signals_dict:
        general_logger.info(
            f"Sending {len(signals_dict)} signals. Actual signals sending is {'enabled' if send_actual else 'disabled'}."
        )

        timestamp_message = add_timestamp_and_separator("")
        await bot.send_message(chat_id, timestamp_message)
        general_logger.info("Sent message with timestamp and separator.")

        for signal in signals_dict.values():
            is_new = signal.count_sends == 0
            is_closed = signal.date_end is not None

            if is_new:
                general_logger.info(f"Detected new signal with ID {signal.id}.")
            elif is_closed:
                general_logger.info(f"Detected closed signal with ID {signal.id}.")
            else:
                general_logger.info(f"Detected actual signal with ID {signal.id}.")

            if is_new or is_closed or send_actual:
                if is_closed:
                    await send_signal_messages(
                        chat_id=chat_id,
                        signals=[signal],
                        format_message_func=format_closed_signal_message,
                        send_timestamp=False
                    )
                    mark_signal_as_reported(signal.id)
                else:
                    await send_signal_messages(
                        chat_id=chat_id,
                        signals=[signal],
                        format_message_func=format_new_signal_message,
                        is_new=is_new,
                        send_timestamp=False
                    )

                success = increment_count_sends(signal.id)
                if success:
                    general_logger.info(
                        f"Successfully incremented count_sends for signal with ID {signal.id}"
                    )
                else:
                    general_logger.warning(
                        f"Failed to increment count_sends for signal with ID {signal.id}"
                    )
                mark_signal_as_sent(signal.id)
            else:
                general_logger.info(
                    f"Skipped actual signal with ID {signal.id} due to sending settings"
                )

        general_logger.info("Signal sending process completed.")
    else:
        general_logger.info("No new signals to send.")
        await bot.send_message(chat_id, "No new signals to send.")
