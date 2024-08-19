import logging
from logging.handlers import TimedRotatingFileHandler
import os
from pathlib import Path

def setup_logging():
    # Создаем директорию logs в корне проекта
    log_dir = Path(__file__).parents[1] / 'logs'
    log_dir.mkdir(exist_ok=True)

    # Настройка общего лога
    general_log_handler = TimedRotatingFileHandler(
        log_dir / 'general.log',
        when="D",
        interval=1,
        backupCount=1
    )
    general_log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

    # Настройка лога анализа
    analyze_log_handler = TimedRotatingFileHandler(
        log_dir / 'analyze.log',
        when="D",
        interval=7,
        backupCount=1
    )
    analyze_log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

    # Закрытие предыдущих обработчиков (если они были настроены)
    if logging.getLogger('general').hasHandlers():
        logging.getLogger('general').handlers.clear()

    if logging.getLogger('analyze').hasHandlers():
        logging.getLogger('analyze').handlers.clear()

    # Настройка общего логгера
    general_logger = logging.getLogger('general')
    general_logger.setLevel(logging.INFO)
    general_logger.addHandler(general_log_handler)

    # Настройка логгера анализа
    analyze_logger = logging.getLogger('analyze')
    analyze_logger.setLevel(logging.INFO)
    analyze_logger.addHandler(analyze_log_handler)

    return general_logger, analyze_logger

general_logger, analyze_logger = setup_logging()

__all__ = ['setup_logging', 'general_logger', 'analyze_logger']