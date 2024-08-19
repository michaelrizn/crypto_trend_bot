from datetime import datetime
from pytz import timezone
from config import CRYPTO_PAIRS, TIMEZONE
from services.signal_manager import check_and_create_signals
from utils.message_formatter import format_new_signal_message, format_closed_signal_message
from database.db_handler import mark_signal_as_reported
from utils.logger import analyze_logger, general_logger
from bot.handlers.commands import actual_send_enabled, bot
from .utils import send_signal_messages

async def perform_check(chat_id=None):
    try:
        analyze_logger.info("Начало выполнения perform_check().")
        new_signals, updated_signals, closed_signals = check_and_create_signals(CRYPTO_PAIRS)

        if chat_id:
            current_time = datetime.now(timezone(TIMEZONE)).strftime("%Y-%m-%d %H:%M")
            separator = "-" * 40
            await bot.send_message(chat_id, f"{current_time}\n{separator}")

            if actual_send_enabled:
                if new_signals:
                    analyze_logger.info(f"Получено {len(new_signals)} новых сигналов.")
                    await send_signal_messages(bot, chat_id, new_signals, format_new_signal_message)

                if closed_signals:
                    analyze_logger.info(f"Получено {len(closed_signals)} закрытых сигналов.")
                    await send_signal_messages(bot, chat_id, closed_signals, format_closed_signal_message)
                    for signal in closed_signals:
                        mark_signal_as_reported(signal[0])
                    analyze_logger.info("Обработаны закрытые сигналы.")

            if updated_signals and not actual_send_enabled:
                analyze_logger.info(f"Обновлено {len(updated_signals)} активных сигналов.")

        analyze_logger.info("Завершено выполнение perform_check().")
    except Exception as e:
        general_logger.error(f"Ошибка при выполнении perform_check: {e}")