import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent.parent / "data" / "astra.db"


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def initialize_memory():
    connection = get_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            memory_type TEXT NOT NULL,
            content TEXT NOT NULL,
            importance INTEGER DEFAULT 5,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()


def save_message(role: str, content: str):
    connection = get_connection()

    connection.execute(
        "INSERT INTO conversations (role, content) VALUES (?, ?)",
        (role, content),
    )

    connection.commit()
    connection.close()


def get_recent_messages(limit: int = 20):
    connection = get_connection()

    rows = connection.execute(
        """
        SELECT role, content
        FROM conversations
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()

    connection.close()

    rows.reverse()

    return [
        {
            "role": role,
            "content": content,
        }
        for role, content in rows
    ]


def save_memory(
    content: str,
    memory_type: str = "general",
    importance: int = 5,
):
    connection = get_connection()

    connection.execute(
        """
        INSERT INTO memories
        (memory_type, content, importance)
        VALUES (?, ?, ?)
        """,
        (memory_type, content, importance),
    )

    connection.commit()
    connection.close()


def get_memories(limit: int = 20):
    connection = get_connection()

    rows = connection.execute(
        """
        SELECT id, memory_type, content, importance
        FROM memories
        ORDER BY importance DESC, updated_at DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()

    connection.close()

    return [
        {
            "id": memory_id,
            "memory_type": memory_type,
            "content": content,
            "importance": importance,
        }
        for memory_id, memory_type, content, importance in rows
    ]
def memory_exists(content: str):
    connection = get_connection()

    row = connection.execute(
        "SELECT id FROM memories WHERE content = ? LIMIT 1",
        (content,),
    ).fetchone()

    connection.close()

    return row is not None
