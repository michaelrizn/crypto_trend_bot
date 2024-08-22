from telebot.async_telebot import AsyncTeleBot
from utils.logger import general_logger
from config import CHECK_INTERVAL, CRYPTO_PAIRS
from bot.scheduler import start_scheduler
from database.db_handler import get_active_signals, get_closed_signals, mark_signal_as_reported
from utils.message_formatter import format_new_signal_message, format_closed_signal_message
from .menu_handlers import get_main_menu_markup  # Проверьте правильность пути и имени файла
from bot.handlers.utils import send_signal_messages
from services.signal_manager import check_and_create_signals

import asyncio

check_task = None

async def start_bot(message, bot: AsyncTeleBot):
    global check_task
    chat_id = message.chat.id  # Получаем chat_id пользователя из сообщения

    if check_task is None or check_task.done():
        general_logger.info("Бот запускается.")
        response = "Бот запущен и готов к работе. Выполняется начальный анализ..."
        await bot.reply_to(message, response, reply_markup=get_main_menu_markup())

        # Выполнить начальный анализ и отправить сигналы
        check_task = asyncio.create_task(process_and_send_signals(bot, chat_id))
        await check_task

        # Запустить планировщик с chat_id
        await start_scheduler(CHECK_INTERVAL, bot, chat_id)

        general_logger.info("Периодическая проверка сигналов запущена.")
        await bot.send_message(chat_id, "Начальный анализ завершен. Бот готов к работе.")
    else:
        general_logger.info("Бот уже работает.")
        response = "Бот уже работает. Используйте кнопки меню для управления."
        await bot.reply_to(message, response, reply_markup=get_main_menu_markup())

async def process_and_send_signals(bot: AsyncTeleBot, chat_id):
    general_logger.info("Выполнение начального анализа и отправка сигналов.")

    # Вызов функции для анализа сигналов
    new_signals, updated_signals, closed_signals = await check_and_create_signals(CRYPTO_PAIRS)

    # Отправка активных сигналов
    if new_signals or updated_signals:
        await bot.send_message(
            chat_id,
            f"Количество активных сигналов: {len(new_signals) + len(updated_signals)}"
        )
        await send_signal_messages(
            chat_id=chat_id,
            signals=new_signals + updated_signals,
            format_message_func=format_new_signal_message
        )

    # Отправка закрытых сигналов
    if closed_signals:
        await bot.send_message(
            chat_id,
            f"Количество закрытых сигналов: {len(closed_signals)}"
        )
        await send_signal_messages(
            chat_id=chat_id,
            signals=closed_signals,
            format_message_func=format_closed_signal_message
        )
        for signal in closed_signals:
            mark_signal_as_reported(signal.id)
        general_logger.info("Закрытые сигналы обработаны и отмечены как отправленные.")
    else:
        await bot.send_message(chat_id, "В данный момент нет закрытых сигналов.")