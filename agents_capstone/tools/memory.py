import sqlite3
import json
import threading
from typing import Any, Optional

DB_PATH = "agents_memory.db"

_lock = threading.Lock()

def _get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with _lock:
        conn = _get_conn()
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS memory (
                user_id TEXT,
                key TEXT,
                value TEXT,
                PRIMARY KEY(user_id, key)
            )
            """
        )
        conn.commit()
        conn.close()

def set_value(user_id: str, key: str, value: Any) -> None:
    json_val = json.dumps(value)
    with _lock:
        conn = _get_conn()
        cur = conn.cursor()
        cur.execute(
            "REPLACE INTO memory (user_id, key, value) VALUES (?, ?, ?)",
            (user_id, key, json_val),
        )
        conn.commit()
        conn.close()

def get_value(user_id: str, key: str) -> Optional[Any]:
    with _lock:
        conn = _get_conn()
        cur = conn.cursor()
        cur.execute("SELECT value FROM memory WHERE user_id=? AND key=?", (user_id, key))
        row = cur.fetchone()
        conn.close()
        if not row:
            return None
        try:
            return json.loads(row["value"])
        except Exception:
            return None

def append_to_list(user_id: str, key: str, item: Any) -> None:
    lst = get_value(user_id, key) or []
    if not isinstance(lst, list):
        lst = [lst]
    lst.append(item)
    set_value(user_id, key, lst)

# initialize DB on import
init_db()
