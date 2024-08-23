import io
import asyncio
from telebot.async_telebot import AsyncTeleBot
from database.models import Signal
from services.crypto_api import get_ohlcv
from utils.chart_generator import generate_chart
from database.db_handler import increment_count_sends, store_signals_for_sending
import logging
from datetime import datetime
from pytz import timezone
from config import TIMEZONE, BOT_TOKEN
from utils.logger import general_logger

bot = AsyncTeleBot(BOT_TOKEN)

async def process_and_store_signals(new_signals, updated_signals, closed_signals):
    store_signals_for_sending(new_signals, updated_signals, closed_signals)
    logging.info(f"Stored for sending: {len(new_signals)} new, {len(updated_signals)} updated, {len(closed_signals)} closed signals.")


async def send_signal_messages(chat_id, signals, format_message_func, is_new=False,
                               send_timestamp=True):
    general_logger.info(f"Started sending messages for {len(signals)} signals.")

    if is_new and signals and send_timestamp:
        current_time = datetime.now(timezone(TIMEZONE)).strftime("%Y-%m-%d %H:%M")
        separator = "-" * 40
        header_message = f"{current_time}\n{separator}"
        try:
            await bot.send_message(chat_id, header_message)
            general_logger.info(f"Sent message with timestamp and separator: {header_message}")
        except Exception as e:
            general_logger.error(f"Error sending header: {e}")
            return

    for signal in signals:
        try:
            # Определяем нужно ли передавать аргумент is_new в format_message_func
            if format_message_func.__name__ == "format_new_signal_message":
                message_text = format_message_func(signal, is_new=is_new)
            else:
                message_text = format_message_func(signal)

            ohlcv_data = await get_ohlcv(signal.name)
            chart_buffer = generate_chart(ohlcv_data, signal.trend, signal.date_start,
                                          signal.date_last)
            chart_bytes = chart_buffer.getvalue()
            general_logger.info(f"Chart for {signal.name} generated successfully.")

            for attempt in range(3):
                try:
                    await asyncio.sleep(1)
                    if chart_bytes:
                        sent_message = await bot.send_photo(chat_id, chart_bytes,
                                                            caption=message_text)
                        general_logger.info(
                            f"Message with chart sent successfully to chat {chat_id}: {sent_message.message_id}")
                    else:
                        sent_message = await bot.send_message(chat_id, message_text)
                        general_logger.info(
                            f"Text message sent to chat {chat_id}: {sent_message.message_id}")

                    # Увеличиваем значение Count Sends после успешной отправки сообщения
                    success = increment_count_sends(signal.id)
                    if success:
                        general_logger.info(
                            f"Successfully incremented count_sends for signal with ID {signal.id}")
                    else:
                        general_logger.warning(
                            f"Failed to increment count_sends for signal with ID {signal.id}")
                    break
                except Exception as e:
                    general_logger.error(
                        f"Error sending message for signal {signal.name} on attempt {attempt + 1}: {e}")
                    if attempt < 2:
                        await asyncio.sleep(5)
                    else:
                        general_logger.error(
                            f"Failed to send message for signal {signal.name} after 3 attempts.")
        except Exception as e:
            general_logger.error(f"Error processing signal {signal.name}: {e}")