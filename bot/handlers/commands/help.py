from telebot.async_telebot import AsyncTeleBot
from utils.logger import general_logger
from .menu_handlers import get_main_menu_markup

async def send_help(message, bot: AsyncTeleBot):
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
    await bot.reply_to(message, help_text, reply_markup=get_main_menu_markup())
    general_logger.info("Справочная информация отправлена.")