import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "voltguard.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            time TEXT,
            voltage REAL,
            current REAL,
            temperature REAL,
            status TEXT,
            risk INTEGER,
            health INTEGER
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            time TEXT,
            status TEXT,
            risk INTEGER,
            voltage REAL,
            temperature REAL
        )
    """)
    conn.commit()
    conn.close()

def insert_reading(v, c, t, status, risk, health):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO readings (time, voltage, current, temperature, status, risk, health) VALUES (?,?,?,?,?,?,?)",
        (datetime.now().strftime("%H:%M:%S"), v, c, t, status, risk, health)
    )
    conn.commit()
    conn.close()

def get_history(limit=60):
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT time, voltage, current, temperature, status, risk, health FROM readings ORDER BY id DESC LIMIT ?",
        (limit,)
    ).fetchall()
    conn.close()
    return [{
        "time": r[0], "voltage": r[1], "current": r[2],
        "temperature": r[3], "status": r[4], "risk": r[5], "health": r[6]
    } for r in reversed(rows)]

def insert_alert(status, risk, voltage, temperature):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO alerts (time, status, risk, voltage, temperature) VALUES (?,?,?,?,?)",
        (datetime.now().strftime("%H:%M:%S"), status, risk, voltage, temperature)
    )
    conn.commit()
    conn.close()

def get_alerts(limit=20):
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT time, status, risk, voltage, temperature FROM alerts ORDER BY id DESC LIMIT ?",
        (limit,)
    ).fetchall()
    conn.close()
    return [{
        "time": r[0], "status": r[1], "risk": r[2],
        "voltage": r[3], "temperature": r[4]
    } for r in rows]

def clear_all():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM readings")
    conn.execute("DELETE FROM alerts")
    conn.commit()
    conn.close()