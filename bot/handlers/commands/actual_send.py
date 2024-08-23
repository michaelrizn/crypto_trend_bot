from config import toggle_actual_signals, get_actual_signals_status
from utils.logger import general_logger

async def toggle_actual_send(message, bot):
    new_status = toggle_actual_signals()
    status = "включена" if new_status else "отключена"
    response = f"Отправка актуальных сигналов {status}."
    await bot.send_message(message.chat.id, response)
    general_logger.info(response)