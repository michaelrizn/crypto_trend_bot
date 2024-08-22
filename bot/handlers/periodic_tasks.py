import logging
from services.signal_manager import check_and_create_signals
from config import CRYPTO_PAIRS


async def perform_check(chat_id, bot):
    logging.info("Выполнение периодической проверки.")
    try:
        new_signals, updated_signals, closed_signals = check_and_create_signals(CRYPTO_PAIRS)

        # Здесь должна быть логика обработки и отправки сигналов
        # Например:
        if new_signals:
            await bot.send_message(chat_id, f"Обнаружено {len(new_signals)} новых сигналов.")
        if closed_signals:
            await bot.send_message(chat_id, f"Закрыто {len(closed_signals)} сигналов.")

    except Exception as e:
        logging.error(f"Ошибка при выполнении периодической проверки: {e}")