from bot.scheduler import update_scheduler_interval, get_current_interval, start_scheduler
from config import CHANNEL_ID

async def change_interval(message, bot):
    command_parts = message.text.split()

    if len(command_parts) == 1:
        current_interval = get_current_interval()
        if current_interval:
            await bot.send_message(message.chat.id,
                                   f"Текущий интервал проверки: {int(current_interval // 60)} минут.")
        else:
            await bot.send_message(message.chat.id, "Планировщик не запущен.")
    elif len(command_parts) == 2:
        try:
            new_interval_minutes = int(command_parts[1])
            if new_interval_minutes <= 0:
                raise ValueError("Интервал должен быть положительным числом.")

            new_interval_seconds = new_interval_minutes * 60
            if get_current_interval() is None:
                await start_scheduler(new_interval_seconds, CHANNEL_ID, bot)
            else:
                update_scheduler_interval(new_interval_seconds)
            await bot.send_message(message.chat.id,
                                   f"Интервал проверки обновлен до {new_interval_minutes} минут.")
        except ValueError as e:
            await bot.send_message(message.chat.id,
                                   f"Ошибка: {str(e)}\nПожалуйста, укажите положительное целое число минут.")
    else:
        await bot.send_message(message.chat.id, "Использование: /interval [число_минут]")