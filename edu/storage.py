import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

class Store:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS attempts (
                id INTEGER PRIMARY KEY, question_id TEXT NOT NULL, choice TEXT NOT NULL,
                reason TEXT NOT NULL, correct INTEGER NOT NULL, diagnosis TEXT,
                ai_json TEXT, created_at TEXT NOT NULL)''')

    @contextmanager
    def connect(self):
        conn = sqlite3.connect(self.path, timeout=5)
        conn.row_factory = sqlite3.Row
        try:
            with conn:
                yield conn
        finally:
            conn.close()

    def save(self, question_id, choice, reason, result, ai):
        with self.connect() as conn:
            cur = conn.execute('INSERT INTO attempts (question_id,choice,reason,correct,diagnosis,ai_json,created_at) VALUES (?,?,?,?,?,?,?)',
                (question_id,choice,reason,int(result['correct']),result['concept'],
                 json.dumps(ai,ensure_ascii=False),datetime.now(timezone.utc).isoformat(timespec='seconds')))
            return cur.lastrowid

    def history(self):
        with self.connect() as conn:
            return [dict(row) for row in conn.execute('SELECT * FROM attempts ORDER BY id')]
