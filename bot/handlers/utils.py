import io
import asyncio
from telebot.async_telebot import AsyncTeleBot
from database.models import Signal
from services.crypto_api import get_ohlcv
from utils.chart_generator import generate_chart
from database.db_handler import increment_count_sends, store_signals_for_sending, get_signals_to_send, get_signal_by_id, mark_signal_as_reported, mark_signal_as_sent
import logging
from datetime import datetime
from pytz import timezone
from config import TIMEZONE, BOT_TOKEN, get_actual_signals_status
from utils.logger import general_logger
from utils.message_formatter import format_closed_signal_message, format_new_signal_message

bot = AsyncTeleBot(BOT_TOKEN)

async def process_and_store_signals(new_signals, updated_signals, closed_signals):
    store_signals_for_sending(new_signals, updated_signals, closed_signals)
    logging.info(f"Сохранено для отправки: {len(new_signals)} новых, {len(updated_signals)} обновленных, {len(closed_signals)} закрытых сигналов.")

async def send_signal_messages(chat_id, signals, format_message_func, is_new=False):
    general_logger.info(f"Начата отправка сообщений для {len(signals)} сигналов.")

    for signal in signals:
        if not is_new and not get_actual_signals_status():
            continue

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

async def send_pending_signals(bot: AsyncTeleBot, chat_id):
    general_logger.info("Обработка отложенных сигналов.")
    signals_to_send = get_signals_to_send()
    send_actual = get_actual_signals_status()

    signals_dict = {}
    for signal_id, signal_type in signals_to_send:
        signal = get_signal_by_id(signal_id)
        if signal:
            signals_dict[signal_id] = signal

    general_logger.info(f"Используем chat_id: {chat_id}")

    if signals_dict:
        general_logger.info(
            f"Отправка {len(signals_dict)} сигналов. Актуальная отправка сигналов "
            f"{'включена' if send_actual else 'выключена'}."
        )

        # Отправляем разделитель только если актуальная отправка выключена и есть сигналы для отправки
        if not send_actual and signals_dict:
            current_time = datetime.now(timezone(TIMEZONE)).strftime("%Y-%m-%d %H:%M")
            separator = "=" * 40
            separator_message = f"{separator}\n{current_time}\n{separator}"
            await bot.send_message(chat_id, separator_message)

        for signal in signals_dict.values():
            is_new = signal.count_sends == 0
            is_closed = signal.date_end is not None

            if is_new:
                general_logger.info(f"Обнаружен новый сигнал с ID {signal.id}.")
            elif is_closed:
                general_logger.info(f"Обнаружен закрытый сигнал с ID {signal.id}.")
            else:
                general_logger.info(f"Обнаружен актуальный сигнал с ID {signal.id}.")

            if is_new or is_closed or send_actual:
                if is_closed:
                    await send_signal_messages(
                        chat_id=chat_id,
                        signals=[signal],
                        format_message_func=format_closed_signal_message,
                    )
                    mark_signal_as_reported(signal.id)
                else:
                    await send_signal_messages(
                        chat_id=chat_id,
                        signals=[signal],
                        format_message_func=format_new_signal_message,
                        is_new=is_new,
                    )

                success = increment_count_sends(signal.id)
                if success:
                    general_logger.info(
                        f"Успешно увеличено количество отправок для сигнала с ID {signal.id}"
                    )
                else:
                    general_logger.warning(
                        f"Не удалось увеличить количество отправок для сигнала с ID {signal.id}"
                    )
                mark_signal_as_sent(signal.id)
            else:
                general_logger.info(
                    f"Пропущен актуальный сигнал с ID {signal.id} из-за настроек отправки"
                )

        general_logger.info("Процесс отправки сигналов завершен.")
    else:
        general_logger.info("Нет новых сигналов для отправки.")
        await bot.send_message(chat_id, "Нет новых сигналов для отправки.")