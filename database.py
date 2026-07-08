import sqlite3
from datetime import datetime
from config import DB_PATH


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            telegram_id INTEGER PRIMARY KEY,
            username TEXT,
            ig_business_id TEXT,
            ig_access_token TEXT,
            ig_username TEXT,
            created_at TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_id INTEGER,
            name TEXT,
            message TEXT,
            button_text TEXT,
            button_url TEXT,
            FOREIGN KEY (owner_id) REFERENCES users(telegram_id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS keywords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_id INTEGER,
            keyword TEXT,
            template_id INTEGER,
            FOREIGN KEY (owner_id) REFERENCES users(telegram_id),
            FOREIGN KEY (template_id) REFERENCES templates(id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS sent_dms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_id INTEGER,
            ig_commenter_username TEXT,
            keyword TEXT,
            sent_at TEXT
        )
    """)

    conn.commit()
    conn.close()


def upsert_user(telegram_id, username):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT telegram_id FROM users WHERE telegram_id = ?", (telegram_id,))
    if c.fetchone() is None:
        c.execute(
            "INSERT INTO users (telegram_id, username, created_at) VALUES (?, ?, ?)",
            (telegram_id, username, datetime.utcnow().isoformat())
        )
    else:
        c.execute("UPDATE users SET username = ? WHERE telegram_id = ?", (username, telegram_id))
    conn.commit()
    conn.close()


def get_user(telegram_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def save_instagram_connection(telegram_id, ig_business_id, ig_access_token, ig_username):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        UPDATE users SET ig_business_id = ?, ig_access_token = ?, ig_username = ?
        WHERE telegram_id = ?
    """, (ig_business_id, ig_access_token, ig_username, telegram_id))
    conn.commit()
    conn.close()


def get_user_by_ig_business_id(ig_business_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE ig_business_id = ?", (ig_business_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def add_template(owner_id, name, message, button_text=None, button_url=None):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        INSERT INTO templates (owner_id, name, message, button_text, button_url)
        VALUES (?, ?, ?, ?, ?)
    """, (owner_id, name, message, button_text, button_url))
    conn.commit()
    tid = c.lastrowid
    conn.close()
    return tid


def get_templates(owner_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM templates WHERE owner_id = ?", (owner_id,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_keyword(owner_id, keyword, template_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        INSERT INTO keywords (owner_id, keyword, template_id) VALUES (?, ?, ?)
    """, (owner_id, keyword.lower().strip(), template_id))
    conn.commit()
    conn.close()


def get_keywords(owner_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM keywords WHERE owner_id = ?", (owner_id,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def find_keyword_match(owner_id, comment_text):
    keywords = get_keywords(owner_id)
    comment_lower = comment_text.lower()
    for kw in keywords:
        if kw["keyword"] in comment_lower:
            return kw
    return None


def record_sent_dm(owner_id, ig_commenter_username, keyword):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        INSERT INTO sent_dms (owner_id, ig_commenter_username, keyword, sent_at)
        VALUES (?, ?, ?, ?)
    """, (owner_id, ig_commenter_username, keyword, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()


def get_stats(owner_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) as total FROM sent_dms WHERE owner_id = ?", (owner_id,))
    total = c.fetchone()["total"]
    conn.close()
    return {"total_dms_sent": total}
