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

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS user_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rut TEXT,
            digito_verificador INTEGER,
            nombre TEXT,
            apellido TEXT,
            email TEXT
        )
        """
    )
    conn.commit()
    conn.close()