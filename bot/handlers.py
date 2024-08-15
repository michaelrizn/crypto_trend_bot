from telebot.async_telebot import AsyncTeleBot
from config import BOT_TOKEN, CRYPTO_PAIRS, CHANNEL_ID
from services.signal_manager import check_and_create_signals, update_active_signals
from database.db_handler import get_active_signals, move_old_signals_to_history, delete_all_tables, \
    init_db, increment_count_sends, get_closed_signals, mark_signal_as_reported
from utils.message_formatter import format_new_signal_message, format_closed_signal_message
from bot.scheduler import start_scheduler, stop_scheduler
from database.models import Signal

bot = AsyncTeleBot(BOT_TOKEN)
scheduler = None


@bot.message_handler(commands=['start'])
async def start_bot(message):
    global scheduler
    if not scheduler or not scheduler.running:
        await bot.reply_to(message, "Запуск бота...")

        await bot.reply_to(message, "Выполняется первичный анализ...")
        await perform_check()

        scheduler = await start_scheduler(perform_check)
        await bot.reply_to(message, "Бот запущен. Анализ будет проводиться каждый час.")

        # Добавляем вызов команды /show после старта
        await show_signals(message)
    else:
        await bot.reply_to(message, "Бот уже запущен.")


@bot.message_handler(commands=['stop'])
async def stop_bot(message):
    global scheduler
    if scheduler and scheduler.running:
        stop_scheduler(scheduler)
        scheduler = None
        await bot.reply_to(message, "Бот остановлен. Ежечасные проверки деактивированы.")
    else:
        await bot.reply_to(message, "Бот не запущен.")


@bot.message_handler(commands=['check'])
async def manual_check(message):
    await bot.reply_to(message, "Инициирована ручная проверка. Пожалуйста, подождите...")
    await perform_check()
    await bot.reply_to(message, "Ручная проверка завершена. Проверьте канал на наличие обновлений.")

    # Добавляем вызов команды /show после ручной проверки
    await show_signals(message)


@bot.message_handler(commands=['show'])
async def show_signals(message):
    active_signals = get_active_signals()
    if not active_signals:
        await bot.reply_to(message, "В данный момент нет активных сигналов.")
    else:
        for signal_tuple in active_signals:
            signal = Signal(*signal_tuple)
            message_text = format_new_signal_message(signal, is_new=signal.count_sends is None)
            await bot.reply_to(message, message_text)
            increment_count_sends(signal.name)


@bot.message_handler(commands=['help'])
async def send_help(message):
    help_text = """
    Доступные команды:
    /start - Запустить бота и активировать ежечасные проверки
    /stop - Остановить бота и деактивировать ежечасные проверки
    /check - Выполнить ручную проверку
    /show - Показать текущие активные сигналы
    /delete_tables - Удалить все таблицы в базе данных (используйте с осторожностью!)
    /help - Показать это сообщение помощи
    """
    await bot.reply_to(message, help_text)


@bot.message_handler(commands=['delete_tables'])
async def delete_tables_command(message):
    try:
        delete_all_tables()
        await bot.reply_to(message, "Все таблицы были удалены.")
        init_db()
        await bot.reply_to(message, "Новые таблицы были созданы.")
    except Exception as e:
        await bot.reply_to(message, f"Произошла ошибка при удалении таблиц: {str(e)}")


async def perform_check():
    print("Начало выполнения perform_check()")
    check_and_create_signals(CRYPTO_PAIRS)
    update_active_signals()

    # Обработка активных сигналов
    active_signals = get_active_signals()
    print(f"Получено {len(active_signals)} активных сигналов")
    for signal_tuple in active_signals:
        signal = Signal(*signal_tuple)
        message = format_new_signal_message(signal, is_new=signal.count_sends is None)
        print(
            f"Подготовлено сообщение о {'новом' if signal.count_sends is None else 'текущем'} сигнале: {signal.name}")

        try:
            sent_message = await bot.send_message(CHANNEL_ID, message)
            print(f"Сообщение успешно отправлено в канал: {sent_message.message_id}")
            increment_count_sends(signal.name)
            print(f"Увеличен счетчик отправок для сигнала: {signal.name}")
        except Exception as e:
            print(f"Ошибка отправки сообщения в канал для сигнала {signal.name}: {e}")

    # Обработка закрытых сигналов
    closed_signals = get_closed_signals()
    print(f"Получено {len(closed_signals)} закрытых сигналов")
    for signal_tuple in closed_signals:
        signal = Signal(*signal_tuple)
        message = format_closed_signal_message(signal)
        print(f"Подготовлено сообщение о закрытом сигнале: {signal.name}")

        try:
            sent_message = await bot.send_message(CHANNEL_ID, message)
            print(
                f"Сообщение о закрытом сигнале успешно отправлено в канал: {sent_message.message_id}")
            mark_signal_as_reported(signal.name)
            print(f"Сигнал {signal.name} помечен как отправленный")
        except Exception as e:
            print(f"Ошибка отправки сообщения о закрытом сигнале {signal.name}: {e}")

    move_old_signals_to_history()
    print("Завершено выполнение perform_check()")


async def setup_bot():
    return bot