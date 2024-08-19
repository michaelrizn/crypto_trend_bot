import logging
import asyncio
import os
from telebot.async_telebot import AsyncTeleBot
from config import BOT_TOKEN, CHECK_INTERVAL as CONFIG_CHECK_INTERVAL, CRYPTO_PAIRS
from database.db_handler import (
    delete_all_tables, get_signals_count, get_active_signals,
    get_closed_signals, mark_signal_as_reported, move_old_signals_to_history,
    fetch_all_signals, init_db
)
from utils.message_formatter import (
    format_new_signal_message, format_closed_signal_message,
    format_signals_table, add_timestamp_and_separator
)
from services.signal_manager import check_and_create_signals
from .utils import send_signal_messages
from utils.logger import setup_logging
from pathlib import Path

# Инициализация логгеров
general_logger, analyze_logger = setup_logging()

bot = AsyncTeleBot(BOT_TOKEN)
CHECK_INTERVAL = CONFIG_CHECK_INTERVAL
actual_send_enabled = True
check_task = None


async def perform_check(chat_id=None):
    try:
        analyze_logger.info("Начало выполнения perform_check().")
        new_signals, updated_signals, closed_signals = check_and_create_signals(CRYPTO_PAIRS)

        if chat_id:
            if actual_send_enabled:
                if new_signals:
                    analyze_logger.info(f"Получено {len(new_signals)} новых сигналов.")
                    await send_signal_messages(bot, chat_id, new_signals, format_new_signal_message,
                                               is_new=True)

                if closed_signals:
                    analyze_logger.info(f"Получено {len(closed_signals)} закрытых сигналов.")
                    await send_signal_messages(bot, chat_id, closed_signals,
                                               format_closed_signal_message)
                    for signal in closed_signals:
                        mark_signal_as_reported(signal[0])
                    analyze_logger.info("Обработаны закрытые сигналы.")

            if updated_signals and not actual_send_enabled:
                analyze_logger.info(f"Обновлено {len(updated_signals)} активных сигналов.")

        move_old_signals_to_history()
        analyze_logger.info("Завершено выполнение perform_check().")
    except Exception as e:
        general_logger.error(f"Ошибка при выполнении perform_check: {e}")


async def start_scheduler(interval, chat_id):
    while True:
        await perform_check(chat_id)
        await asyncio.sleep(interval)


@bot.message_handler(commands=['delete_tables'])
async def delete_tables(message):
    general_logger.info("Запущена команда /delete_tables.")
    delete_all_tables()
    init_db()
    await bot.reply_to(message, "Все таблицы были удалены и заново созданы.")
    general_logger.info("Все таблицы удалены и заново созданы.")


@bot.message_handler(commands=['count'])
async def count_signals(message):
    general_logger.info("Запущена команда /count.")
    active_count, closed_count = get_signals_count()
    await bot.reply_to(message,
                       f"Количество открытых сигналов: {active_count}\n"
                       f"Количество закрытых сигналов: {closed_count}")
    general_logger.info(
        f"Количество открытых сигналов: {active_count}, закрытых сигналов: {closed_count}")


@bot.message_handler(commands=['show'])
async def show_signals(message):
    general_logger.info("Запущена команда /show.")
    active_signals = get_active_signals()
    if not active_signals:
        general_logger.info("Нет активных сигналов.")
        await bot.reply_to(message, "В данный момент нет активных сигналов.")
    else:
        await send_signal_messages(bot, message.chat.id, active_signals, format_new_signal_message)

    closed_signals = get_closed_signals()
    if closed_signals:
        await send_signal_messages(bot, message.chat.id, closed_signals,
                                   format_closed_signal_message)
        for signal in closed_signals:
            mark_signal_as_reported(signal[0])
        general_logger.info("Закрытые сигналы обработаны и отмечены как отправленные.")
    else:
        general_logger.info("Нет закрытых сигналов.")
        await bot.reply_to(message, "В данный момент нет закрытых сигналов.")


@bot.message_handler(commands=['table_signals'])
async def table_signals(message):
    general_logger.info("Запущена команда /table_signals.")
    signals = fetch_all_signals()
    if not signals:
        await bot.reply_to(message, "Таблица `signals` пуста.")
        general_logger.info("Таблица `signals` пуста.")
    else:
        table_message = format_signals_table(signals)
        table_message = add_timestamp_and_separator(table_message)
        await bot.reply_to(message, table_message)
        general_logger.info("Таблица `signals` отправлена.")


@bot.message_handler(commands=['actual_send'])
async def toggle_actual_send(message):
    global actual_send_enabled
    actual_send_enabled = not actual_send_enabled
    status = "включена" if actual_send_enabled else "выключена"
    response = f"Отправка новых и закрытых сигналов {status}. Актуальные сигналы не будут отправляться."
    response = add_timestamp_and_separator(response)
    await bot.reply_to(message, response)
    general_logger.info(f"Отправка новых и закрытых сигналов {status}.")


@bot.message_handler(commands=['interval'])
async def change_interval(message):
    global CHECK_INTERVAL, check_task
    args = message.text.split()
    if len(args) == 1:
        minutes = CHECK_INTERVAL // 60
        response = f"Текущий интервал проверки: {minutes} минут. Чтобы изменить, используйте /interval <число минут>"
        response = add_timestamp_and_separator(response)
        await bot.reply_to(message, response)
        general_logger.info(f"Сообщение о текущем интервале проверки ({minutes} минут) отправлено.")
    elif len(args) == 2:
        try:
            new_interval_minutes = int(args[1])
            if new_interval_minutes < 1:
                await bot.reply_to(message, "Интервал не может быть меньше 1 минуты")
                general_logger.info("Ошибка: введен интервал меньше 1 минуты.")
            else:
                CHECK_INTERVAL = new_interval_minutes * 60
                response = f"Интервал проверки изменен на {new_interval_minutes} минут"
                response = add_timestamp_and_separator(response)
                await bot.reply_to(message, response)
                general_logger.info(f"Интервал проверки изменен на {new_interval_minutes} минут.")

                if check_task and not check_task.done():
                    check_task.cancel()
                    try:
                        await check_task
                    except asyncio.CancelledError:
                        pass

                check_task = asyncio.create_task(start_scheduler(CHECK_INTERVAL, message.chat.id))
                general_logger.info("Задача с обновленным интервалом успешно запущена.")
        except ValueError:
            await bot.reply_to(message, "Пожалуйста, введите корректное число минут")
            general_logger.info("Ошибка: введено некорректное значение интервала.")


@bot.message_handler(commands=['start'])
async def start_bot(message):
    global check_task
    if check_task is None or check_task.done():
        general_logger.info("Запуск бота.")
        response = "Запуск бота..."
        response = add_timestamp_and_separator(response)
        await bot.reply_to(message, response)
        check_task = asyncio.create_task(start_scheduler(CHECK_INTERVAL, message.chat.id))
        general_logger.info("Периодическая проверка запущена.")
    else:
        general_logger.info("Бот уже запущен.")
        response = "Бот уже запущен."
        response = add_timestamp_and_separator(response)
        await bot.reply_to(message, response)


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
        general_logger.info("Бот остановлен. Периодические проверки деактивированы.")
        response = "Бот остановлен. Периодические проверки деактивированы."
        response = add_timestamp_and_separator(response)
        await bot.reply_to(message, response)
    else:
        general_logger.info("Бот не запущен.")
        response = "Бот не запущен."
        response = add_timestamp_and_separator(response)
        await bot.reply_to(message, response)


@bot.message_handler(commands=['help'])
async def send_help(message):
    general_logger.info("Отправка справочной информации.")
    help_text = """
    Доступные команды:
    /start - Запустить бота и активировать периодические проверки
    /stop - Остановить бота и деактивировать периодические проверки
    /show - Показать текущие активные и закрытые сигналы
    /count - Показать количество открытых и закрытых сигналов
    /delete_tables - Удалить все таблицы в базе данных (используйте с осторожностью!)
    /table_signals - Показать содержимое таблицы `signals`
    /help - Показать это сообщение помощи
    /interval - Изменить интервал проверки или показать текущий интервал
    /actual_send - Включить/выключить отправку актуальных сигналов
    /logs - Показать файлы логов
    /delete_logs - Удалить все файлы логов (используйте с осторожностью!)
    """
    help_text = add_timestamp_and_separator(help_text)
    await bot.reply_to(message, help_text)
    general_logger.info("Справочная информация отправлена.")


@bot.message_handler(commands=['logs'])
async def send_logs(message):
    general_logger.info("Запрос логов через команду /logs")
    try:
        log_dir = Path(__file__).parents[2] / 'logs'
        with open(log_dir / 'general.log', 'rb') as general_log, open(log_dir / 'analyze.log',
                                                                      'rb') as analyze_log:
            await bot.send_document(message.chat.id, general_log, caption="Общий лог")
            await bot.send_document(message.chat.id, analyze_log, caption="Лог анализа")
    except Exception as e:
        general_logger.error(f"Ошибка при отправке логов: {e}")
        response = "Произошла ошибка при отправке логов."
        response = add_timestamp_and_separator(response)
        await bot.reply_to(message, response)


@bot.message_handler(commands=['delete_logs'])
async def delete_logs(message):
    general_logger.info("Запущена команда /delete_logs")
    try:
        log_dir = Path(__file__).parents[2] / 'logs'
        deleted_files = 0
        for file in os.listdir(log_dir):
            if file.endswith(".log"):
                os.remove(os.path.join(log_dir, file))
                deleted_files += 1

        # Создаем новые пустые файлы логов
        open(log_dir / 'general.log', 'w').close()
        open(log_dir / 'analyze.log', 'w').close()

        # Переинициализируем логгеры
        new_general_logger, new_analyze_logger = setup_logging()

        # Обновляем глобальные переменные в модуле utils.logger
        import utils.logger
        utils.logger.general_logger = new_general_logger
        utils.logger.analyze_logger = new_analyze_logger

        response = f"Удалено файлов логов: {deleted_files}. Созданы новые пустые файлы логов."
        response = add_timestamp_and_separator(response)
        await bot.reply_to(message, response)
        new_general_logger.info(
            f"Удалено {deleted_files} файлов логов. Созданы новые пустые файлы.")
    except Exception as e:
        general_logger.error(f"Ошибка при удалении логов: {e}")
        response = "Произошла ошибка при удалении логов."
        response = add_timestamp_and_separator(response)
        await bot.reply_to(message, response)