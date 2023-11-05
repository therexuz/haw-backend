import sqlite3
import json

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
        CREATE TABLE IF NOT EXISTS actuadores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_led TEXT,
            topic TEXT,
            status INTEGER
        )
        """
    )
    
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS estudiante (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rut TEXT,
            nombre TEXT,
            apellido TEXT,
            correo TEXT
        )
        """
    )
    
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS preguntas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT,
            pregunta TEXT,
            respuesta TEXT,
            alternativas TEXT
        )
        """
    )
    
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS respuestas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rut TEXT,
            id_pregunta INTEGER,
            respuesta BOOL
        )
        """
    )
    
    # Agregar bateria de preguntas a Preguntas
    with open('preguntas.json', 'r') as json_file:
        data = json.load(json_file)
        
    for pregunta in data:
        pregunta_actual = pregunta['pregunta'],
        cursor.execute("SELECT COUNT(*) FROM preguntas WHERE pregunta=?", pregunta_actual)
        count = cursor.fetchone()[0]
        if count == 0:
            alternativas_str = "&".join(pregunta["alternativas"])
            cursor.execute("INSERT INTO preguntas (tipo, pregunta, respuesta, alternativas) VALUES (?, ?, ?, ?)",
                       (pregunta['tipo'], pregunta['pregunta'], pregunta['respuesta'], alternativas_str))        
    
    conn.commit()
    conn.close()