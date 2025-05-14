# indexer.py
import sqlite3, json, os
from analysis import apply_rules

DATABASE_URL = os.getenv("DATABASE_URL", "database.db")

def create_tables():
    conn = sqlite3.connect(DATABASE_URL)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            log_id INTEGER,
            rule_triggered TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

create_tables()

def process_log(log_message):
    conn = sqlite3.connect(DATABASE_URL)
    c = conn.cursor()
    c.execute("INSERT INTO logs (message) VALUES (?)", (log_message,))
    log_id = c.lastrowid
    conn.commit()

    # Apply rules
    try:
        with open("rules.json", "r") as f:
            rules = json.load(f)
        matched_rule = apply_rules.check_rules(log_message, rules)
        if matched_rule:
            c.execute("INSERT INTO alerts (log_id, rule_triggered) VALUES (?, ?)", (log_id, matched_rule))
            conn.commit()
    except Exception as e:
        print(f"Rule processing error: {e}")

    conn.close()
