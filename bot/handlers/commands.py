import logging
import asyncio
from telebot.async_telebot import AsyncTeleBot
from config import BOT_TOKEN, CHECK_INTERVAL as CONFIG_CHECK_INTERVAL, CRYPTO_PAIRS
from database.db_handler import delete_all_tables, get_signals_count, get_active_signals, \
    get_closed_signals, mark_signal_as_reported, move_old_signals_to_history, fetch_all_signals
from utils.message_formatter import format_new_signal_message, format_closed_signal_message, \
    format_signals_table
from services.signal_manager import check_and_create_signals, update_active_signals
from .utils import send_signal_messages
from database.db_handler import delete_all_tables, get_signals_count, get_active_signals, get_closed_signals, mark_signal_as_reported, move_old_signals_to_history, fetch_all_signals, init_db

bot = AsyncTeleBot(BOT_TOKEN)
CHECK_INTERVAL = CONFIG_CHECK_INTERVAL
actual_send_enabled = True  # Переменная для контроля отправки актуальных сигналов
check_task = None  # Глобальная переменная для хранения задачи периодической проверки


async def perform_check(chat_id=None):
    try:
        logging.info("Начало выполнения perform_check().")
        check_and_create_signals(CRYPTO_PAIRS)
        update_active_signals()

        active_signals = get_active_signals()
        logging.info(f"Получено {len(active_signals)} активных сигналов.")
        if active_signals and actual_send_enabled:
            await send_signal_messages(bot, chat_id, active_signals, format_new_signal_message)

        closed_signals = get_closed_signals()
        logging.info(f"Получено {len(closed_signals)} закрытых сигналов.")
        if closed_signals:
            if chat_id:
                await send_signal_messages(bot, chat_id, closed_signals,
                                           format_closed_signal_message)
            for signal in closed_signals:
                mark_signal_as_reported(signal[0])
            logging.info("Закрытые сигналы обработаны.")

        move_old_signals_to_history()
        logging.info("Завершено выполнение perform_check().")
    except Exception as e:
        logging.error(f"Ошибка при выполнении perform_check: {e}")


async def start_scheduler(interval, chat_id):
    global check_task
    while True:
        await perform_check(chat_id)
        await asyncio.sleep(interval)


@bot.message_handler(commands=['delete_tables'])
async def delete_tables(message):
    logging.info("Запущена команда /delete_tables.")
    delete_all_tables()
    init_db()  # Повторная инициализация базы данных после удаления таблиц
    await bot.reply_to(message, "Все таблицы были удалены и заново созданы.")
    logging.info("Все таблицы удалены и заново созданы.")

@bot.message_handler(commands=['count'])
async def count_signals(message):
    logging.info("Запущена команда /count.")
    active_count, closed_count = get_signals_count()
    await bot.reply_to(message,
                       f"Количество открытых сигналов: {active_count}\nКоличество закрытых сигналов: {closed_count}")
    logging.info(f"Количество открытых сигналов: {active_count}, закрытых сигналов: {closed_count}")


@bot.message_handler(commands=['show'])
async def show_signals(message):
    logging.info("Запущена команда /show.")
    active_signals = get_active_signals()
    if not active_signals:
        logging.info("Нет активных сигналов.")
        await bot.reply_to(message, "В данный момент нет активных сигналов.")
    else:
        await send_signal_messages(bot, message.chat.id, active_signals, format_new_signal_message)

    closed_signals = get_closed_signals()
    if closed_signals:
        await send_signal_messages(bot, message.chat.id, closed_signals,
                                   format_closed_signal_message)
        for signal in closed_signals:
            mark_signal_as_reported(signal[0])
        logging.info("Закрытые сигналы обработаны и отмечены как отправленные.")
    else:
        logging.info("Нет закрытых сигналов.")
        await bot.reply_to(message, "В данный момент нет закрытых сигналов.")


@bot.message_handler(commands=['table_signals'])
async def table_signals(message):
    logging.info("Запущена команда /table_signals.")
    signals = fetch_all_signals()
    if not signals:
        await bot.reply_to(message, "Таблица `signals` пуста.")
        logging.info("Таблица `signals` пуста.")
    else:
        table_message = format_signals_table(signals)
        await bot.reply_to(message, table_message)
        logging.info("Таблица `signals` отправлена.")


@bot.message_handler(commands=['actual_send'])
async def toggle_actual_send(message):
    global actual_send_enabled
    actual_send_enabled = not actual_send_enabled
    status = "включена" if actual_send_enabled else "выключена"
    await bot.reply_to(message, f"Отправка актуальных сигналов {status}.")
    logging.info(f"Отправка актуальных сигналов {status}.")


@bot.message_handler(commands=['interval'])
async def change_interval(message):
    global CHECK_INTERVAL, check_task
    args = message.text.split()
    if len(args) == 1:
        minutes = CHECK_INTERVAL // 60
        await bot.reply_to(message,
                           f"Текущий интервал проверки: {minutes} минут. Чтобы изменить, используйте /interval <число минут>")
        logging.info(f"Сообщение о текущем интервале проверки ({minutes} минут) отправлено.")
    elif len(args) == 2:
        try:
            new_interval_minutes = int(args[1])
            if new_interval_minutes < 1:
                await bot.reply_to(message, "Интервал не может быть меньше 1 минуты")
                logging.info("Ошибка: введен интервал меньше 1 минуты.")
            else:
                CHECK_INTERVAL = new_interval_minutes * 60
                await bot.reply_to(message,
                                   f"Интервал проверки изменен на {new_interval_minutes} минут")
                logging.info(f"Интервал проверки изменен на {new_interval_minutes} минут.")

                # Остановка текущей задачи и запуск новой
                if check_task and not check_task.done():
                    check_task.cancel()
                    try:
                        await check_task
                    except asyncio.CancelledError:
                        pass

                # Запуск новой задачи с обновленным интервалом
                check_task = asyncio.create_task(start_scheduler(CHECK_INTERVAL, message.chat.id))
                logging.info("Задача с обновленным интервалом успешно запущена.")
        except ValueError:
            await bot.reply_to(message, "Пожалуйста, введите корректное число минут")
            logging.info("Ошибка: введено некорректное значение интервала.")


@bot.message_handler(commands=['start'])
async def start_bot(message):
    global check_task
    if check_task is None or check_task.done():
        logging.info("Запуск бота.")
        await bot.reply_to(message, "Запуск бота...")
        check_task = asyncio.create_task(start_scheduler(CHECK_INTERVAL, message.chat.id))
        logging.info("Периодическая проверка запущена.")
    else:
        logging.info("Бот уже запущен.")
        await bot.reply_to(message, "Бот уже запущен.")


@bot.message_handler(commands=['stop'])
async def stop_bot(message):
    global check_task
    if check_task and not check_task.done():
        check_task.cancel()
        try:
            await check_task
        except asyncio.CancelledError:
            pass
        check_task = None
        logging.info("Бот остановлен. Периодические проверки деактивированы.")
        await bot.reply_to(message, "Бот остановлен. Периодические проверки деактивированы.")
    else:
        logging.info("Бот не запущен.")
        await bot.reply_to(message, "Бот не запущен.")


@bot.message_handler(commands=['help'])
async def send_help(message):
    logging.info("Отправка справочной информации.")
    help_text = """
    Доступные команды:
    /start - Запустить бота и активировать периодические проверки
    /stop - Остановить бота и деактивировать периодические проверки
    /check - Выполнить ручную проверку
    /show - Показать текущие активные и закрытые сигналы
    /count - Показать количество открытых и закрытых сигналов
    /delete_tables - Удалить все таблицы в базе данных (используйте с осторожностью!)
    /table_signals - Показать содержимое таблицы `signals`
    /help - Показать это сообщение помощи
    /interval - Изменить интервал проверки или показать текущий интервал
    /actual_send - Включить/выключить отправку актуальных сигналов
    """
    await bot.reply_to(message, help_text)
    logging.info("Справочная информация отправлена.")