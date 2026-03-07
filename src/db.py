import sqlite3
import os
import time
from pathlib import Path


DATA_DIR = Path.home() / ".splleing-analysis"
DB_PATH = DATA_DIR / "words.db"

BATCH_SIZE = 10
FLUSH_INTERVAL = 5


def ensure_db() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute(
        "CREATE TABLE IF NOT EXISTS words ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "word TEXT NOT NULL, "
        "timestamp TEXT NOT NULL"
        ")"
    )
    conn.commit()
    os.chmod(DB_PATH, 0o600)
    return conn


class WordBuffer:
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn
        self._buffer: list[tuple[str, str]] = []
        self._last_flush = time.time()

    def add(self, word: str) -> None:
        from datetime import datetime, timezone

        self._buffer.append((word, datetime.now(timezone.utc).isoformat()))
        if len(self._buffer) >= BATCH_SIZE or (time.time() - self._last_flush) >= FLUSH_INTERVAL:
            self.flush()

    def flush(self) -> None:
        if not self._buffer:
            return
        self._conn.executemany(
            "INSERT INTO words (word, timestamp) VALUES (?, ?)",
            self._buffer,
        )
        self._conn.commit()
        self._buffer.clear()
        self._last_flush = time.time()
