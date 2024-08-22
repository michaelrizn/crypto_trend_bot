from database.models import Signal
import sqlite3
from config import DB_NAME
from utils.logger import general_logger
from typing import Any

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS signals
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT,
                  trend TEXT,
                  date_start TEXT,
                  date_last TEXT,
                  accuracy INTEGER CHECK(accuracy >= 1 AND accuracy <= 100),
                  date_end TEXT,
                  price_start REAL,
                  price_last REAL,
                  price_end REAL,
                  count_sends INTEGER,
                  reported INTEGER DEFAULT 0)''')

    c.execute('''CREATE TABLE IF NOT EXISTS history
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT,
                  trend TEXT,
                  date_start TEXT,
                  date_last TEXT,
                  accuracy INTEGER CHECK(accuracy >= 1 AND accuracy <= 100),
                  date_end TEXT,
                  price_start REAL,
                  price_last REAL,
                  price_end REAL,
                  count_sends INTEGER,
                  reported INTEGER)''')

    conn.commit()
    conn.close()

def delete_all_tables():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("DROP TABLE IF EXISTS signals")
    c.execute("DROP TABLE IF EXISTS history")

    conn.commit()
    conn.close()

def insert_signal(name, trend, date_start, price_start, accuracy):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute('''SELECT * FROM signals 
                 WHERE name = ? AND date_end IS NULL''', (name,))
    existing_signal = c.fetchone()

    if not existing_signal:
        accuracy = max(1, min(100, int(accuracy)))
        c.execute('''INSERT INTO signals 
                     (name, trend, date_start, date_last, accuracy, price_start, price_last, count_sends)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                  (name, trend, date_start, date_start, accuracy, price_start, price_start, 0))

    conn.commit()
    conn.close()

def update_signal(name, date_last, price_last, accuracy):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    accuracy = max(1, min(100, int(accuracy)))
    c.execute('''UPDATE signals
                 SET date_last = ?, price_last = ?, accuracy = ?
                 WHERE name = ? AND date_end IS NULL''',
              (date_last, price_last, accuracy, name))
    conn.commit()
    conn.close()

def increment_count_sends(signal_id: Any) -> bool:
    """
    Increment the count_sends for a signal.
    This function is used externally.
    """
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''UPDATE signals
                 SET count_sends = count_sends + 1
                 WHERE id = ?''', (signal_id,))
    conn.commit()
    rows_affected = c.rowcount
    conn.close()
    general_logger.info(f"Увеличено count_sends для сигнала с ID {signal_id}. Затронуто строк: {rows_affected}")
    return rows_affected > 0

def get_active_signals():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''SELECT id, name, trend, date_start, date_last, accuracy, date_end, 
                 price_start, price_last, price_end, count_sends, reported 
                 FROM signals WHERE date_end IS NULL''')
    signals = c.fetchall()
    conn.close()
    return [Signal(*signal) for signal in signals]

def get_closed_signals():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''SELECT id, name, trend, date_start, date_last, accuracy, date_end, 
                 price_start, price_last, price_end, count_sends, reported 
                 FROM signals 
                 WHERE date_end IS NOT NULL 
                 AND reported = 0''')
    signals = c.fetchall()
    conn.close()
    return signals

def close_signal(name, date_end, price_end):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''UPDATE signals
                 SET date_end = ?, price_end = ?
                 WHERE name = ? AND date_end IS NULL''',
              (date_end, price_end, name))
    conn.commit()
    conn.close()

def mark_signal_as_reported(signal_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''UPDATE signals
                 SET reported = 1
                 WHERE id = ?''', (signal_id,))
    conn.commit()
    conn.close()

def move_old_signals_to_history():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''INSERT INTO history
                 SELECT * FROM signals
                 WHERE date_end IS NOT NULL 
                 AND reported = 1''')
    c.execute('''DELETE FROM signals
                 WHERE date_end IS NOT NULL 
                 AND reported = 1''')
    conn.commit()
    conn.close()

def get_signals_count():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM signals WHERE date_end IS NULL")
    active_count = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM signals WHERE date_end IS NOT NULL")
    closed_count = c.fetchone()[0]
    conn.close()
    return active_count, closed_count

def fetch_all_signals():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM signals")
    signals = c.fetchall()
    conn.close()
    return signals

def get_active_signal(name):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''SELECT id, name, trend, date_start, date_last, accuracy, date_end, 
                 price_start, price_last, price_end, count_sends, reported 
                 FROM signals 
                 WHERE name = ? AND date_end IS NULL''', (name,))
    signal_data = c.fetchone()
    conn.close()
    return Signal(*signal_data) if signal_data else None

def store_signals_for_sending(new_signals, updated_signals, closed_signals):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS signals_to_send
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  signal_id INTEGER,
                  signal_type TEXT,
                  sent INTEGER DEFAULT 0)''')

    for signal in new_signals:
        c.execute("INSERT INTO signals_to_send (signal_id, signal_type) VALUES (?, ?)",
                  (signal.id, "new"))

    for signal in updated_signals:
        c.execute("INSERT INTO signals_to_send (signal_id, signal_type) VALUES (?, ?)",
                  (signal.id, "updated"))

    for signal in closed_signals:
        c.execute("INSERT INTO signals_to_send (signal_id, signal_type) VALUES (?, ?)",
                  (signal.id, "closed"))

    conn.commit()
    conn.close()

def get_signals_to_send():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("SELECT signal_id, signal_type FROM signals_to_send WHERE sent = 0")
    signals_to_send = c.fetchall()

    conn.close()

    return signals_to_send

def mark_signal_as_sent(signal_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''UPDATE signals_to_send
                 SET sent = 1
                 WHERE signal_id = ?''', (signal_id,))
    conn.commit()
    conn.close()
    general_logger.info(f"Сигнал с ID {signal_id} отмечен как отправленный")

def get_signal_by_id(signal_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM signals WHERE id = ?", (signal_id,))
    signal_data = c.fetchone()
    conn.close()
    if signal_data:
        return Signal(*signal_data)
    return None

__all__ = ['increment_count_sends']