import sqlite3
from datetime import datetime

class AlertStore:
    """
    Manages SQLite storage of alerts.
    """
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY,
                timestamp TEXT,
                node TEXT,
                sensor TEXT,
                image_path TEXT,
                description TEXT
            )
        """
        )
        conn.commit()
        conn.close()

    def add_alert(self, node: str, sensor: str, image_path: str, description: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO alerts(timestamp, node, sensor, image_path, description)
            VALUES (?, ?, ?, ?, ?)
            """,
            (datetime.now().isoformat(), node, sensor, image_path, description),
        )
        conn.commit()
        conn.close()

    def get_alerts(self, limit: int = 20):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, timestamp, node, sensor, image_path, description"
            " FROM alerts ORDER BY id DESC LIMIT ?",
            (limit,),
        )
        rows = cursor.fetchall()
        conn.close()
        return [
            dict(
                id=row[0],
                timestamp=row[1],
                node=row[2],
                sensor=row[3],
                image_path=row[4],
                description=row[5],
            )
            for row in rows
        ]
