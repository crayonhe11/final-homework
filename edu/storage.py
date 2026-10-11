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
                ai_json TEXT, created_at TEXT NOT NULL, hints_used INTEGER)''')

            columns = {row['name'] for row in conn.execute('PRAGMA table_info(attempts)')}
            if 'hints_used' not in columns:
                conn.execute('ALTER TABLE attempts ADD COLUMN hints_used INTEGER')
            if 'course_concept' not in columns:
                conn.execute('ALTER TABLE attempts ADD COLUMN course_concept TEXT')
            conn.execute('CREATE TABLE IF NOT EXISTS lesson_reads (concept_id TEXT PRIMARY KEY, read_at TEXT NOT NULL)')
            conn.execute('CREATE INDEX IF NOT EXISTS attempts_question_id ON attempts(question_id, id)')
            conn.execute('CREATE TABLE IF NOT EXISTS code_drafts (task_id TEXT PRIMARY KEY, source TEXT NOT NULL, updated_at TEXT NOT NULL)')
            conn.execute('CREATE TABLE IF NOT EXISTS code_attempts (id INTEGER PRIMARY KEY, task_id TEXT NOT NULL, source TEXT NOT NULL, mode TEXT NOT NULL, passed INTEGER NOT NULL, result_json TEXT NOT NULL, created_at TEXT NOT NULL)')


    @contextmanager
    def connect(self):
        conn = sqlite3.connect(self.path, timeout=5)
        conn.row_factory = sqlite3.Row
        try:
            with conn:
                yield conn
        finally:
            conn.close()

    def save(self, question_id, choice, reason, result, ai, hints_used=0, course_concept=None):
        if type(hints_used) is not int or hints_used < 0:
            raise ValueError("提示次数必须是非负整数")
        with self.connect() as conn:
            cur = conn.execute('INSERT INTO attempts (question_id,choice,reason,correct,diagnosis,ai_json,created_at,hints_used,course_concept) VALUES (?,?,?,?,?,?,?,?,?)',
                (question_id,choice,reason,int(result['correct']),result['concept'],
                 json.dumps(ai,ensure_ascii=False),datetime.now(timezone.utc).isoformat(timespec='seconds'),hints_used,course_concept))
            return cur.lastrowid

    def history(self):
        with self.connect() as conn:
            return [dict(row) for row in conn.execute('SELECT * FROM attempts ORDER BY id')]

    def mark_lesson_read(self, concept_id):
        with self.connect() as conn:
            conn.execute('INSERT OR IGNORE INTO lesson_reads (concept_id,read_at) VALUES (?,?)',
                         (concept_id,datetime.now(timezone.utc).isoformat()))

    def lesson_reads(self):
        with self.connect() as conn:
            return {row['concept_id']:row['read_at'] for row in conn.execute('SELECT * FROM lesson_reads')}

    def save_draft(self, task_id, source):
        with self.connect() as conn:
            conn.execute('INSERT INTO code_drafts VALUES (?,?,?) ON CONFLICT(task_id) DO UPDATE SET source=excluded.source,updated_at=excluded.updated_at',
                         (task_id,source,datetime.now(timezone.utc).isoformat(timespec='seconds')))

    def get_draft(self, task_id):
        with self.connect() as conn:
            row=conn.execute('SELECT source FROM code_drafts WHERE task_id=?',(task_id,)).fetchone()
            return None if row is None else row['source']

    def save_code_attempt(self, task_id, source, mode, result):
        with self.connect() as conn:
            conn.execute('INSERT INTO code_attempts (task_id,source,mode,passed,result_json,created_at) VALUES (?,?,?,?,?,?)',
                         (task_id,source,mode,int(bool(result.get('passed'))),json.dumps(result,ensure_ascii=False),datetime.now(timezone.utc).isoformat(timespec='seconds')))

    def code_history(self):
        with self.connect() as conn:
            return [dict(row) for row in conn.execute('SELECT * FROM code_attempts ORDER BY id')]
