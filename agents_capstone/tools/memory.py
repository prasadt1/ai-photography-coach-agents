"""
Persistent Memory Layer: SQLite-backed session storage with ADK compatibility.

Purpose:
- Persist user sessions across app restarts
- Enable conversation continuity (users can close/reopen app)
- Provide foundation for cloud deployment with Google Agent Development Kit

Architecture Pattern: Adapter Pattern
- Current: SQLite for local development
- Future: Easy migration to Google Cloud Memory Store via same interface
- ADK-compatible: set_value(), get_value(), append_to_list() match ADK Memory API

Thread Safety: Uses threading.Lock() for concurrent access protection
Data Format: JSON serialization for complex objects (dicts, lists)

Production Note: For cloud deployment, replace SQLite with Cloud SQL or Firestore
while keeping the same function signatures.
"""

import sqlite3
import json
import threading
from typing import Any, Optional

# SQLite database file (created automatically in project root)
DB_PATH = "agents_memory.db"

# Thread lock for concurrent access protection
# Prevents race conditions when multiple users access memory simultaneously
_lock = threading.Lock()

def _get_conn():
    """Get thread-safe database connection.
    
    Configuration:
    - check_same_thread=False: Allows connection across threads
    - row_factory=sqlite3.Row: Returns dict-like rows for easier access
    """
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database schema on first run.
    
    Table Structure:
    - user_id: Session identifier (e.g., "user123")
    - key: Data key (e.g., "session", "preferences")
    - value: JSON-serialized data
    - PRIMARY KEY(user_id, key): One value per user+key combination
    
    Design: Simple key-value store, mimics ADK Memory API structure
    """
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
    """Store or update a value in memory.
    
    ADK-Compatible API: Matches Google Agent Development Kit Memory.set() signature
    
    Args:
        user_id: Session identifier
        key: Data key (e.g., "session", "history")
        value: Any JSON-serializable object (dict, list, string, etc.)
    
    Implementation:
    - Serializes value to JSON string
    - Uses REPLACE to insert or update
    - Thread-safe with lock
    """
    json_val = json.dumps(value)
    with _lock:
        conn = _get_conn()
        cur = conn.cursor()
        # REPLACE = INSERT or UPDATE if (user_id, key) already exists
        cur.execute(
            "REPLACE INTO memory (user_id, key, value) VALUES (?, ?, ?)",
            (user_id, key, json_val),
        )
        conn.commit()
        conn.close()

def get_value(user_id: str, key: str) -> Optional[Any]:
    """Retrieve a value from memory.
    
    ADK-Compatible API: Matches Google Agent Development Kit Memory.get() signature
    
    Args:
        user_id: Session identifier
        key: Data key
        
    Returns:
        Deserialized value (dict, list, etc.) or None if not found
    
    Error Handling: Returns None if JSON parsing fails (corrupt data)
    """
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
            # Graceful degradation if JSON is corrupted
            return None

def append_to_list(user_id: str, key: str, item: Any) -> None:
    """Append item to a list stored in memory.
    
    Convenience method for managing list-based data (e.g., conversation history)
    
    Args:
        user_id: Session identifier
        key: Data key
        item: Item to append
    
    Behavior:
    - Creates new list if key doesn't exist
    - Converts non-list values to list before appending
    - Thread-safe (uses set_value internally)
    """
    lst = get_value(user_id, key) or []
    if not isinstance(lst, list):
        lst = [lst]
    lst.append(item)
    set_value(user_id, key, lst)

# Initialize database schema on module import
# This ensures the memory table exists before any operations
init_db()
