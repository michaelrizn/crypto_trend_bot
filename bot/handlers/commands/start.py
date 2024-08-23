from telebot.async_telebot import AsyncTeleBot
from utils.logger import general_logger
from config import CHECK_INTERVAL, CRYPTO_PAIRS
from bot.scheduler import start_scheduler
from database.db_handler import get_active_signals, get_closed_signals, mark_signal_as_reported
from utils.message_formatter import format_new_signal_message, format_closed_signal_message
from .menu_handlers import get_main_menu_markup
from bot.handlers.utils import send_signal_messages
from services.signal_manager import check_and_create_signals

import asyncio

check_task = None

async def start_bot(message, bot: AsyncTeleBot):
    global check_task
    chat_id = message.chat.id

    if check_task is None or check_task.done():
        general_logger.info("Бот запускается.")
        response = "Бот запущен и готов к работе. Выполняется начальный анализ..."
        await bot.reply_to(message, response, reply_markup=get_main_menu_markup())

        check_task = asyncio.create_task(process_and_send_signals(bot, chat_id))
        await check_task

        await start_scheduler(CHECK_INTERVAL, bot, chat_id)

        general_logger.info("Периодическая проверка сигналов запущена.")
        await bot.send_message(chat_id, "Начальный анализ завершен. Бот готов к работе.")
    else:
        general_logger.info("Бот уже работает.")
        response = "Бот уже работает. Используйте кнопки меню для управления."
        await bot.reply_to(message, response, reply_markup=get_main_menu_markup())

async def process_and_send_signals(bot: AsyncTeleBot, chat_id):
    general_logger.info("Выполнение начального анализа и отправка сигналов.")

    new_signals, updated_signals, closed_signals = await check_and_create_signals(CRYPTO_PAIRS)

    if new_signals or updated_signals:
        await bot.send_message(
            chat_id,
            f"Количество активных сигналов: {len(new_signals) + len(updated_signals)}"
        )
        await send_signal_messages(
            chat_id=chat_id,
            signals=new_signals + updated_signals,
            format_message_func=format_new_signal_message,
            is_new=True
        )

    if closed_signals:
        await bot.send_message(
            chat_id,
            f"Количество закрытых сигналов: {len(closed_signals)}"
        )
        for signal in closed_signals:
            try:
                if signal.price_end is not None and signal.price_start is not None:
                    message = format_closed_signal_message(signal)
                    await bot.send_message(chat_id, message)
                    mark_signal_as_reported(signal.id)
                else:
                    general_logger.warning(f"Пропущен закрытый сигнал {signal.name} из-за отсутствия данных о цене")
            except Exception as e:
                general_logger.error(f"Ошибка при обработке закрытого сигнала {signal.name}: {e}")
        general_logger.info("Закрытые сигналы обработаны и отмечены как отправленные.")
    else:
        await bot.send_message(chat_id, "В данный момент нет закрытых сигналов.")

    # Обработка существующих закрытых сигналов, которые еще не были отправлены
    existing_closed_signals = get_closed_signals()
    if existing_closed_signals:
        await bot.send_message(
            chat_id,
            f"Количество существующих закрытых сигналов: {len(existing_closed_signals)}"
        )
        for signal in existing_closed_signals:
            try:
                if signal.price_end is not None and signal.price_start is not None:
                    message = format_closed_signal_message(signal)
                    await bot.send_message(chat_id, message)
                    mark_signal_as_reported(signal.id)
                else:
                    general_logger.warning(f"Пропущен существующий закрытый сигнал {signal.name} из-за отсутствия данных о цене")
            except Exception as e:
                general_logger.error(f"Ошибка при обработке существующего закрытого сигнала {signal.name}: {e}")
        general_logger.info("Существующие закрытые сигналы обработаны и отмечены как отправленные.")