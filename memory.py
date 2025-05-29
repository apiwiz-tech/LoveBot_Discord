import sqlite3
from datetime import datetime, timedelta
from types import SimpleNamespace

class MemoryStore:
    def __init__(self, db_path='memory.db'):
        self.conn = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        self._setup()

    def _setup(self):
        c = self.conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            author TEXT,
            content TEXT,
            timestamp TIMESTAMP
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS analysis (
            msg_id TEXT,
            analysis TEXT,
            FOREIGN KEY(msg_id) REFERENCES messages(id)
        )''')
        self.conn.commit()

    def log_message(self, message):
        c = self.conn.cursor()
        c.execute('INSERT OR IGNORE INTO messages VALUES (?, ?, ?, ?)', (
            str(message.id), message.author.name, message.content, message.created_at))
        self.conn.commit()

    def store_analysis(self, message, analysis):
        c = self.conn.cursor()
        c.execute('INSERT INTO analysis VALUES (?, ?)', (str(message.id), analysis))
        self.conn.commit()

    def get_recent(self, days=7):
        cutoff = datetime.utcnow() - timedelta(days=days)
        c = self.conn.cursor()
        c.execute('SELECT id, author, content FROM messages WHERE timestamp >= ?', (cutoff,))
        rows = c.fetchall()
        return [SimpleNamespace(id=row[0], author=row[1], content=row[2]) for row in rows]

    def get_all(self):
        c = self.conn.cursor()
        c.execute('SELECT id, author, content FROM messages')
        rows = c.fetchall()
        return [SimpleNamespace(id=row[0], author=row[1], content=row[2]) for row in rows]

    def get_last_messages_content(self, limit=10):
        c = self.conn.cursor()
        c.execute('SELECT content FROM messages ORDER BY timestamp DESC LIMIT ?', (limit,))
        rows = c.fetchall()
        return [row[0] for row in rows]

    def generate_intervention(self, message):
        recent = self.get_last_messages_content(limit=5)
        return f"I notice tension here. Let's reflect:\n" + '\n'.join(recent)

    def explain_conflict(self):
        # placeholder method (will be replaced by GPT method)
        return "It seems you're both frustrated; try active listening and acknowledging feelings."
