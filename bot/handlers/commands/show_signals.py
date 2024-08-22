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
    general_logger.info("Команда /show запущена.")
    chat_id = message.chat.id

    # Получение активных сигналов
    active_signals = get_active_signals()
    if not active_signals:
        general_logger.info("Активных сигналов нет.")
        await bot.reply_to(message, "В данный момент нет активных сигналов.")
    else:
        general_logger.info(f"Найдено {len(active_signals)} активных сигналов.")
        await send_signal_messages(
            chat_id=chat_id, signals=active_signals, format_message_func=format_new_signal_message
        )

    # Получение закрытых сигналов
    closed_signals = get_closed_signals()
    if closed_signals:
        general_logger.info(f"Найдено {len(closed_signals)} закрытых сигналов.")
        await send_signal_messages(
            chat_id=chat_id, signals=closed_signals, format_message_func=format_closed_signal_message
        )
        for signal in closed_signals:
            mark_signal_as_reported(signal[0])
        general_logger.info("Закрытые сигналы обработаны и отмечены как отправленные.")
    else:
        general_logger.info("Закрытых сигналов нет.")
        await bot.reply_to(message, "В данный момент нет закрытых сигналов.")

async def send_pending_signals(bot: AsyncTeleBot, chat_id):
    general_logger.info("Обработка ожидающих сигналов.")
    signals_to_send = get_signals_to_send()
    send_actual = get_actual_signals_status()

    signals_dict = {}
    for signal_id, signal_type in signals_to_send:
        signal = get_signal_by_id(signal_id)
        if signal:
            signals_dict[signal_id] = signal

    general_logger.info(f"Используемый chat_id: {chat_id}")

    if signals_dict:
        general_logger.info(
            f"Отправка {len(signals_dict)} сигналов. Отправка актуальных сигналов {'включена' if send_actual else 'выключена'}.")

        if send_actual:
            timestamp_message = add_timestamp_and_separator("")
            await bot.send_message(chat_id, timestamp_message)
            general_logger.info("Отправлено сообщение с временной меткой и разделителем.")

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
                        f"Успешно увеличено count_sends для сигнала с ID {signal.id}")
                else:
                    general_logger.warning(
                        f"Не удалось увеличить count_sends для сигнала с ID {signal.id}")
                mark_signal_as_sent(signal.id)
            else:
                general_logger.info(
                    f"Пропущен актуальный сигнал с ID {signal.id} из-за настроек отправки")

        general_logger.info("Обработка отправки сигналов завершена.")
    else:
        general_logger.info("Новых сигналов для отправки нет.")
        await bot.send_message(chat_id, "Новых сигналов для отправки нет.")