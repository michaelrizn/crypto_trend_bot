from .commands import (
    start_bot,
    start_scheduler_command,
    stop_bot,
    show_signals,
    count_signals,
    delete_tables,
    table_signals,
    toggle_actual_send,
    change_interval,
    send_help,
    send_logs,
    delete_logs,
    send_pending_signals
)
from .commands.menu_handlers import (
    get_main_menu_markup,
    show_signals_button,
    count_signals_button,
    start_bot_button,
    stop_bot_button,
    help_button
)


async def setup_bot(bot):
    bot.message_handler(commands=['start'])(
        lambda message: start_bot(message, bot)
    )
    bot.message_handler(commands=['scheduler_start'])(
        lambda message: start_scheduler_command(message, bot)
    )
    bot.message_handler(commands=['stop'])(
        lambda message: stop_bot(message, bot)
    )
    bot.message_handler(commands=['show'])(
        lambda message: show_signals(message, bot)
    )
    bot.message_handler(commands=['count'])(
        lambda message: count_signals(message, bot)
    )
    bot.message_handler(commands=['delete_tables'])(
        lambda message: delete_tables(message, bot)
    )
    bot.message_handler(commands=['table_signals'])(
        lambda message: table_signals(message, bot)
    )
    bot.message_handler(commands=['actual_send'])(
        lambda message: toggle_actual_send(message, bot)
    )
    bot.message_handler(commands=['interval'])(
        lambda message: change_interval(message, bot)
    )
    bot.message_handler(commands=['help'])(
        lambda message: send_help(message, bot)
    )
    bot.message_handler(commands=['logs'])(
        lambda message: send_logs(message, bot)
    )
    bot.message_handler(commands=['delete_logs'])(
        lambda message: delete_logs(message, bot)
    )
    bot.message_handler(commands=['send_signals'])(
        lambda message: send_pending_signals(message, bot)
    )

    bot.message_handler(func=lambda message: message.text == "📊 Показать сигналы")(
        lambda message: show_signals_button(message, bot)
    )
    bot.message_handler(func=lambda message: message.text == "🔢 Количество сигналов")(
        lambda message: count_signals_button(message, bot)
    )
    bot.message_handler(func=lambda message: message.text == "▶️ Старт")(
        lambda message: start_bot_button(message, bot)
    )
    bot.message_handler(func=lambda message: message.text == "⏹ Стоп")(
        lambda message: stop_bot_button(message, bot)
    )
    bot.message_handler(func=lambda message: message.text == "❓ Помощь")(
        lambda message: help_button(message, bot)
    )

    return bot