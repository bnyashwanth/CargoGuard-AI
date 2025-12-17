import sqlite3

def get_db():
    return sqlite3.connect("db/cargoguard.db", check_same_thread=False)

def init_db():
    db = get_db()
    c = db.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS shipments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        origin TEXT,
        destination TEXT,
        weight REAL,
        risk REAL,
        best_route TEXT,
        created_at TEXT
    )
    """)

    db.commit()
    db.close()
