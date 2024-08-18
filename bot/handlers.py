import asyncio
from telebot.async_telebot import AsyncTeleBot
from telebot import apihelper
from config import BOT_TOKEN, CRYPTO_PAIRS, CHECK_INTERVAL
from services.signal_manager import check_and_create_signals, update_active_signals
from database.db_handler import get_active_signals, move_old_signals_to_history, delete_all_tables, \
    init_db, increment_count_sends, get_closed_signals, mark_signal_as_reported, get_signals_count
from utils.message_formatter import format_new_signal_message, format_closed_signal_message
from database.models import Signal
import logging
import aiohttp

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

apihelper.SESSION_TIMEOUT = 60  # Увеличить таймаут в секундах

bot = AsyncTeleBot(BOT_TOKEN)
check_task = None

async def send_signal_messages(chat_id, signals, format_message_func):
    async with aiohttp.ClientSession() as session:
        for signal_tuple in signals:
            signal = Signal(*signal_tuple)
            message_text = format_message_func(signal)
            for attempt in range(3):  # Делаем до 3 попыток отправки сообщения
                try:
                    await asyncio.sleep(1)  # Добавляем задержку в 1 секунду перед отправкой каждого сообщения
                    sent_message = await bot.send_message(chat_id, message_text)
                    logging.info(f"Сообщение успешно отправлено в чат {chat_id}: {sent_message.message_id}")
                    increment_count_sends(signal.name)
                    break  # Если сообщение отправлено успешно, выходим из цикла попыток
                except Exception as e:
                    logging.error(f"Ошибка отправки сообщения для сигнала {signal.name} на попытке {attempt + 1}: {e}")
                    if attempt < 2:
                        await asyncio.sleep(5)  # Ждем 5 секунд перед повторной попыткой

async def periodic_check(chat_id):
    while True:
        await perform_check(chat_id)
        await asyncio.sleep(CHECK_INTERVAL)

@bot.message_handler(commands=['start'])
async def start_bot(message):
    global check_task
    if check_task is None or check_task.done():
        logging.info("Запуск бота.")
        await bot.reply_to(message, "Запуск бота...")

        # Выполняем первичный анализ
        await perform_check(message.chat.id)

        # Сообщаем пользователю, что бот запущен, и планировщик настроен
        await bot.reply_to(message, "Бот запущен.")
        logging.info("Периодическая проверка запущена.")

        # Запуск периодической проверки
        check_task = asyncio.create_task(periodic_check(message.chat.id))
    else:
        logging.info("Бот уже запущен.")
        await bot.reply_to(message, "Бот уже запущен.")

@bot.message_handler(commands=['stop'])
async def stop_bot(message):
    global check_task
    if check_task and not check_task.done():
        check_task.cancel()
        check_task = None
        logging.info("Бот остановлен. Периодические проверки деактивированы.")
        await bot.reply_to(message, "Бот остановлен. Периодические проверки деактивированы.")
    else:
        logging.info("Бот не запущен.")
        await bot.reply_to(message, "Бот не запущен.")

@bot.message_handler(commands=['check'])
async def manual_check(message):
    logging.info("Инициирована ручная проверка.")
    await bot.reply_to(message, "Инициирована ручная проверка. Пожалуйста, подождите...")
    await perform_check(message.chat.id)
    await bot.reply_to(message, "Ручная проверка завершена. Проверьте канал на наличие обновлений.")
    logging.info("Ручная проверка завершена.")

@bot.message_handler(commands=['show'])
async def show_signals(message):
    if message is None:
        logging.error("Передан пустой объект message.")
        return

    logging.info("Отображение текущих сигналов.")
    active_signals = get_active_signals()
    if not active_signals:
        logging.info("Нет активных сигналов.")
        await bot.reply_to(message, "В данный момент нет активных сигналов.")
    else:
        await send_signal_messages(message.chat.id, active_signals, format_new_signal_message)

    closed_signals = get_closed_signals()
    if closed_signals:
        await send_signal_messages(message.chat.id, closed_signals, format_closed_signal_message)
        for signal in closed_signals:
            mark_signal_as_reported(signal[1])
        logging.info("Обработаны закрытые сигналы.")

@bot.message_handler(commands=['help'])
async def send_help(message):
    if message is None:
        logging.error("Передан пустой объект message.")
        return

    logging.info("Отправка справочной информации.")
    help_text = """
    Доступные команды:
    /start - Запустить бота и активировать периодические проверки
    /stop - Остановить бота и деактивировать периодические проверки
    /check - Выполнить ручную проверку
    /show - Показать текущие активные и закрытые сигналы
    /count - Показать количество открытых и закрытых сигналов
    /delete_tables - Удалить все таблицы в базе данных (используйте с осторожностью!)
    /help - Показать это сообщение помощи
    """
    await bot.reply_to(message, help_text)

@bot.message_handler(commands=['delete_tables'])
async def delete_tables_command(message):
    try:
        delete_all_tables()
        logging.info("Все таблицы были удалены.")
        await bot.reply_to(message, "Все таблицы были удалены.")
        init_db()
        logging.info("Новые таблицы были созданы.")
        await bot.reply_to(message, "Новые таблицы были созданы.")
    except Exception as e:
        logging.error(f"Произошла ошибка при удалении таблиц: {e}")
        await bot.reply_to(message, f"Произошла ошибка при удалении таблиц: {str(e)}")

@bot.message_handler(commands=['count'])
async def count_signals(message):
    if message is None:
        logging.error("Передан пустой объект message.")
        return

    active_count, closed_count = get_signals_count()
    logging.info(f"Количество открытых сигналов: {active_count}, закрытых сигналов: {closed_count}")
    await bot.reply_to(message, f"Количество открытых сигналов: {active_count}\nКоличество закрытых сигналов: {closed_count}")

async def perform_check(chat_id=None):
    try:
        logging.info("Начало выполнения perform_check().")
        check_and_create_signals(CRYPTO_PAIRS)
        update_active_signals()

        if chat_id:
            active_signals = get_active_signals()
            logging.info(f"Получено {len(active_signals)} активных сигналов.")
            await send_signal_messages(chat_id, active_signals, format_new_signal_message)

            closed_signals = get_closed_signals()
            logging.info(f"Получено {len(closed_signals)} закрытых сигналов.")
            await send_signal_messages(chat_id, closed_signals, format_closed_signal_message)

        move_old_signals_to_history()
        logging.info("Завершено выполнение perform_check().")
    except Exception as e:
        logging.error(f"Ошибка при выполнении perform_check: {e}")

async def setup_bot():
    logging.info("Настройка бота.")
    return bot