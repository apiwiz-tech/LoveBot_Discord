
### `memory.py`
python
import sqlite3
from datetime import datetime, timedelta

class MemoryStore:
    def __init__(self, db_path='memory.db'):
        self.conn = sqlite3.connect(db_path)
        self._setup()

    def _setup(self):
        c = self.conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS messages (id TEXT PRIMARY KEY, author TEXT, content TEXT, timestamp DATETIME)''')
        c.execute('''CREATE TABLE IF NOT EXISTS analysis (msg_id TEXT, analysis TEXT)''')
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
        c.execute('SELECT * FROM messages WHERE timestamp >= ?', (cutoff,))
        return [SimpleNamespace(id=row[0], author=row[1], content=row[2]) for row in c.fetchall()]

    def get_all(self):
        c = self.conn.cursor()
        c.execute('SELECT * FROM messages')
        return [SimpleNamespace(id=row[0], author=row[1], content=row[2]) for row in c.fetchall()]

    def generate_intervention(self, message):
        # Simple reflection: fetch last 5 messages
        c = self.conn.cursor()
        c.execute('SELECT content FROM messages ORDER BY timestamp DESC LIMIT 5')
        recent = '\n'.join(row[0] for row in c.fetchall())
        return f"I notice tension here. Let's reflect:\n{recent}"  

    def explain_conflict(self):
        # placeholder
        return "It seems you're both frustrated; try active listening and acknowledging feelings."
