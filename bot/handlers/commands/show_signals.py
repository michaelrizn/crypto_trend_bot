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

    # Отправка сообщения с текущим временем и разделителем перед отправкой сигналов
    timestamp_message = add_timestamp_and_separator("")
    await bot.send_message(chat_id, timestamp_message)
    general_logger.info("Отправлено сообщение с отметкой времени и разделителем.")

    active_signals = get_active_signals()
    if not active_signals:
        general_logger.info("No active signals.")
        await bot.reply_to(message, "В данный момент нет активных сигналов.")
    else:
        general_logger.info(f"Found {len(active_signals)} active signals.")
        await send_signal_messages(
            chat_id=chat_id, signals=active_signals, format_message_func=format_new_signal_message
        )

    closed_signals = get_closed_signals()
    if closed_signals:
        general_logger.info(f"Found {len(closed_signals)} закрытых сигналов.")
        await send_signal_messages(
            chat_id=chat_id,
            signals=closed_signals,
            format_message_func=format_closed_signal_message
        )
        for signal in closed_signals:
            mark_signal_as_reported(signal.id)
        general_logger.info("Закрытые сигналы обработаны и отмечены как отправленные.")
    else:
        general_logger.info("Нет закрытых сигналов.")
        await bot.reply_to(message, "В данный момент нет закрытых сигналов.")

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
            f"Sending {len(signals_dict)} сигналов. Актуальная отправка сигналов "
            f"{'включена' if send_actual else 'выключена'}."
        )

        timestamp_message = add_timestamp_and_separator("")
        await bot.send_message(chat_id, timestamp_message)
        general_logger.info("Отправлено сообщение с отметкой времени и разделителем.")

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