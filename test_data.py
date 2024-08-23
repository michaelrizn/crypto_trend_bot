from database.db_handler import insert_signal, update_signal, close_signal, init_db, update_db_structure
from datetime import datetime, timedelta

def add_test_data():
    init_db()  # Ensure the database is initialized
    update_db_structure()  # Update the database structure if needed

    now = datetime.now()

    # Новый сигнал BTC/USDT
    insert_signal("BTC/USDT", "bullish", now.isoformat(), 50000, 80, "upward")

    # Актуальный сигнал ETH/USDT
    eth_start = now - timedelta(days=2)
    insert_signal("ETH/USDT", "bearish", eth_start.isoformat(), 3000, 75, "downward")
    update_signal("ETH/USDT", now.isoformat(), 2900, 78, "stable")

    # Закрытый сигнал ADA/USDT
    ada_start = now - timedelta(days=5)
    ada_end = now - timedelta(days=1)
    insert_signal("ADA/USDT", "bullish", ada_start.isoformat(), 1.2, 70, "upward")
    update_signal("ADA/USDT", ada_end.isoformat(), 1.3, 72, "downward")
    close_signal("ADA/USDT", now.isoformat(), 1.25)

if __name__ == "__main__":
    add_test_data()
    print("Test data added to the database.")