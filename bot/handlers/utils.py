import io
import asyncio
from telebot.async_telebot import AsyncTeleBot
from database.models import Signal
from services.crypto_api import get_ohlcv
from utils.chart_generator import generate_chart
from database.db_handler import increment_count_sends
import logging

async def send_signal_messages(bot: AsyncTeleBot, chat_id, signals, format_message_func):
    logging.info(f"Начата отправка сообщений по {len(signals)} сигналам.")
    for signal_tuple in signals:
        signal = Signal(*signal_tuple)
        message_text = format_message_func(signal)
        try:
            ohlcv_data = get_ohlcv(signal.name)
            chart = generate_chart(ohlcv_data, signal.trend)
            logging.info(f"График для {signal.name} успешно сгенерирован.")
        except Exception as e:
            logging.error(f"Ошибка при генерации графика для {signal.name}: {e}")
            chart = None

        for attempt in range(3):
            try:
                await asyncio.sleep(1)
                if chart:
                    with io.BytesIO(chart) as photo:
                        photo.name = f"{signal.name}_chart.png"
                        sent_message = await bot.send_photo(chat_id, photo, caption=message_text)
                    logging.info(f"Сообщение с графиком успешно отправлено в чат {chat_id}: {sent_message.message_id}")
                else:
                    sent_message = await bot.send_message(chat_id, message_text)
                    logging.info(f"Текстовое сообщение отправлено в чат {chat_id}: {sent_message.message_id}")
                increment_count_sends(signal.name)
                break
            except Exception as e:
                logging.error(f"Ошибка отправки сообщения для сигнала {signal.name} на попытке {attempt + 1}: {e}")
                if attempt < 2:
                    await asyncio.sleep(5)
                else:
                    logging.error(f"Не удалось отправить сообщение для сигнала {signal.name} после 3 попыток.")
                    try:
                        sent_message = await bot.send_message(chat_id, message_text)
                        logging.info(f"Отправлено текстовое сообщение без графика: {sent_message.message_id}")
                    except Exception as text_error:
                        logging.error(f"Не удалось отправить даже текстовое сообщение: {text_error}")