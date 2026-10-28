"""SQLite state with optimistic revisions; each browser has its own opaque session."""
from contextlib import contextmanager
import json
import sqlite3
from pathlib import Path
from .domain import empty_state

class ConflictError(Exception):
    pass

class Store:
    def __init__(self, path):
        self.path = str(path)
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.execute('CREATE TABLE IF NOT EXISTS learners (id TEXT PRIMARY KEY, revision INTEGER NOT NULL, state TEXT NOT NULL)')

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=10)
        try:
            with db:
                yield db
        finally:
            db.close()

    def get(self, user):
        with self.connect() as db:
            row = db.execute('SELECT revision,state FROM learners WHERE id=?', (user,)).fetchone()
        return (row[0], json.loads(row[1])) if row else (0, empty_state())

    def save(self, user, revision, state):
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            current = db.execute('SELECT revision FROM learners WHERE id=?', (user,)).fetchone()
            if (current[0] if current else 0) != revision:
                raise ConflictError('另一页面已修改进度，请先导出当前记录，再刷新或重新导入。')
            new = revision + 1
            db.execute('INSERT INTO learners VALUES (?,?,?) ON CONFLICT(id) DO UPDATE SET revision=excluded.revision,state=excluded.state',
                       (user, new, json.dumps(state, ensure_ascii=False)))
        return new
