import io
import asyncio
from telebot.async_telebot import AsyncTeleBot
from database.models import Signal
from services.crypto_api import get_ohlcv
from utils.chart_generator import generate_chart
from database.db_handler import increment_count_sends
import logging
from datetime import datetime
from pytz import timezone
from config import TIMEZONE

async def send_signal_messages(bot: AsyncTeleBot, chat_id, signals, format_message_func,
                               is_new=False):
    logging.info(f"Начата отправка сообщений по {len(signals)} сигналам.")

    if signals:  # Проверка на наличие сигналов
        # Отправляем временную метку и разделитель
        current_time = datetime.now(timezone(TIMEZONE)).strftime("%Y-%m-%d %H:%M")
        separator = "-" * 40
        header_message = f"{current_time}\n{separator}"
        await bot.send_message(chat_id, header_message)
        logging.info(f"Отправлено сообщение с временной меткой и разделителем: {header_message}")

    for signal_tuple in signals:
        try:
            signal = Signal(*signal_tuple)
        except TypeError as e:
            logging.error(f"Ошибка при создании объекта Signal: {e}")
            continue

        message_text = format_message_func(signal, is_new=is_new)
        try:
            ohlcv_data = get_ohlcv(signal.name)
            chart_buffer = generate_chart(ohlcv_data, signal.trend, signal.date_start,
                                          signal.date_end)
            chart_bytes = chart_buffer.getvalue()
            logging.info(f"График для {signal.name} успешно сгенерирован.")
        except Exception as e:
            logging.error(f"Ошибка при генерации графика для {signal.name}: {e}")
            chart_bytes = None

        for attempt in range(3):
            try:
                await asyncio.sleep(1)
                if chart_bytes:
                    sent_message = await bot.send_photo(chat_id, chart_bytes, caption=message_text)
                    logging.info(
                        f"Сообщение с графиком успешно отправлено в чат {chat_id}: {sent_message.message_id}")
                else:
                    sent_message = await bot.send_message(chat_id, message_text)
                    logging.info(
                        f"Текстовое сообщение отправлено в чат {chat_id}: {sent_message.message_id}")
                increment_count_sends(signal.name)
                break
            except Exception as e:
                logging.error(
                    f"Ошибка отправки сообщения для сигнала {signal.name} на попытке {attempt + 1}: {e}")
                if attempt < 2:
                    await asyncio.sleep(5)
                else:
                    logging.error(
                        f"Не удалось отправить сообщение для сигнала {signal.name} после 3 попыток.")
                    try:
                        sent_message = await bot.send_message(chat_id, message_text)
                        logging.info(
                            f"Отправлено текстовое сообщение без графика: {sent_message.message_id}")
                    except Exception as text_error:
                        logging.error(
                            f"Не удалось отправить даже текстовое сообщение: {text_error}")
