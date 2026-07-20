import sqlite3
import datetime

class ManifestDB:
    def __init__(self, db_path="manifest.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._create_table()

    def _create_table(self):
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS files (
                file_id TEXT PRIMARY KEY,
                original_name TEXT,
                upload_time TEXT
                )
            ''')
        self.conn.commit()

    def add_file(self, file_id, original_name):
        timestamp = datetime.datetime.now().isoformat()
        self.conn.execute(""
                          "INSERT INTO files VALUES (?,?,?)",
                          (file_id, original_name, timestamp)
        )
        self.conn.commit()
