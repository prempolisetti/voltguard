import sqlite3
from datetime import datetime

DB_PATH = "voltguard.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            voltage REAL,
            current REAL,
            temperature REAL,
            status TEXT,
            risk INTEGER,
            health INTEGER,
            time TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            status TEXT,
            risk INTEGER,
            voltage REAL,
            temperature REAL,
            time TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    conn.commit()
    conn.close()


def insert_reading(voltage, current, temperature, status, risk, health):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO readings (voltage, current, temperature, status, risk, health, time)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (voltage, current, temperature, status, risk, health, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def get_history(limit=20):
    conn = get_connection()
    cur = conn.cursor()
    rows = cur.execute(
        """
        SELECT id, voltage, current, temperature, status, risk, health, time
        FROM readings
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def insert_alert(status, risk, voltage, temperature):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO alerts (status, risk, voltage, temperature, time)
        VALUES (?, ?, ?, ?, ?)
        """,
        (status, risk, voltage, temperature, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def get_alerts(limit=20):
    conn = get_connection()
    cur = conn.cursor()
    rows = cur.execute(
        """
        SELECT id, status, risk, voltage, temperature, time
        FROM alerts
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def clear_all():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM readings")
    cur.execute("DELETE FROM alerts")
    conn.commit()
    conn.close()
