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
    logging.info(f"Сохранено для отправки: {len(new_signals)} новых, {len(updated_signals)} обновленных, {len(closed_signals)} закрытых сигналов.")


async def send_signal_messages(chat_id, signals, format_message_func, is_new=False,
                               send_timestamp=True):
    general_logger.info(f"Начата отправка сообщений для {len(signals)} сигналов.")

    if is_new and signals and send_timestamp:
        current_time = datetime.now(timezone(TIMEZONE)).strftime("%Y-%m-%d %H:%М")
        separator = "-" * 40
        header_message = f"{current_time}\n{separator}"
        try:
            await bot.send_message(chat_id, header_message)
            general_logger.info(f"Отправлено сообщение с отметкой времени и разделителем: {header_message}")
        except Exception as e:
            general_logger.error(f"Ошибка при отправке заголовка: {e}")
            return

    for signal in signals:
        try:
            if format_message_func.__name__ == "format_new_signal_message":
                message_text = format_message_func(signal, is_new=is_new)
            else:
                message_text = format_message_func(signal)

            ohlcv_data = await get_ohlcv(signal.name)
            chart_buffer = generate_chart(ohlcv_data, signal.trend, signal.date_start,
                                          signal.date_last)
            chart_bytes = chart_buffer.getvalue()
            general_logger.info(f"График для {signal.name} успешно создан.")

            for attempt in range(3):
                try:
                    await asyncio.sleep(1)
                    if chart_bytes:
                        sent_message = await bot.send_photo(chat_id, chart_bytes,
                                                            caption=message_text)
                        general_logger.info(
                            f"Сообщение с графиком успешно отправлено в чат {chat_id}: {sent_message.message_id}")
                    else:
                        sent_message = await bot.send_message(chat_id, message_text)
                        general_logger.info(
                            f"Текстовое сообщение отправлено в чат {chat_id}: {sent_message.message_id}")

                    success = increment_count_sends(signal.id)
                    if success:
                        general_logger.info(
                            f"Успешно увеличено количество отправок для сигнала с ID {signal.id}")
                    else:
                        general_logger.warning(
                            f"Не удалось увеличить количество отправок для сигнала с ID {signal.id}")
                    break
                except Exception as e:
                    general_logger.error(
                        f"Ошибка при отправке сообщения для сигнала {signal.name} на попытке {attempt + 1}: {e}")
                    if attempt < 2:
                        await asyncio.sleep(5)
                    else:
                        general_logger.error(
                            f"Не удалось отправить сообщение для сигнала {signal.name} после 3 попыток.")
        except Exception as e:
            general_logger.error(f"Ошибка при обработке сигнала {signal.name}: {e}")