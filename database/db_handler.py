import sqlite3
from config import DB_NAME

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

def increment_count_sends(name):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''UPDATE signals
                 SET count_sends = CASE
                     WHEN count_sends IS NULL THEN 1
                     ELSE count_sends + 1
                 END
                 WHERE name = ? AND date_end IS NULL''', (name,))
    conn.commit()
    conn.close()

def get_active_signals():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''SELECT id, name, trend, date_start, date_last, accuracy, date_end, 
                 price_start, price_last, price_end, count_sends, reported 
                 FROM signals WHERE date_end IS NULL''')
    signals = c.fetchall()
    conn.close()
    return signals

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