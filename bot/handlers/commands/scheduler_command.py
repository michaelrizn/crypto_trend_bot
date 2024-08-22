import logging
from bot.scheduler import start_scheduler, get_current_interval
from config import CHECK_INTERVAL

async def start_scheduler_command(message, bot):
    try:
        # Получаем текущий интервал, если планировщик уже запущен
        current_interval = get_current_interval()

        if current_interval is None:
            # Если планировщик не запущен, запускаем его с интервалом из конфигурации
            await start_scheduler(CHECK_INTERVAL, bot)
            await bot.reply_to(message, f"Планировщик успешно запущен с интервалом {CHECK_INTERVAL} секунд.")
            logging.info("Планировщик успешно запущен.")
        else:
            # Если планировщик уже запущен, уведомляем пользователя
            await bot.reply_to(message, f"Планировщик уже запущен с интервалом {current_interval} секунд.")
            logging.info(f"Попытка запуска планировщика, но он уже запущен с интервалом {current_interval} секунд.")
    except Exception as e:
        logging.error(f"Ошибка при запуске планировщика: {e}")
        await bot.reply_to(message, "Произошла ошибка при запуске планировщика.")