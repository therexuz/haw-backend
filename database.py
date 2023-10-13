import sqlite3

def init_db():
    conn = sqlite3.connect("home_automation_wizard.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT,
            timestamp DATETIME,
            value REAL
        )
        """
    )
    conn.commit()
    conn.close()