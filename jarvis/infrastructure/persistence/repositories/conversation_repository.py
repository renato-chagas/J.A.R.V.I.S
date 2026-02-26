import sqlite3


class ConversationRepository:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def save(self, user_input: str, bot_response: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO conversations (user_input, bot_response) VALUES (?, ?)",
            (user_input, bot_response),
        )
        conn.commit()
        conn.close()

    def list_all(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, user_input, bot_response FROM conversations")
        list = cursor.fetchall()
        conn.close()
        return list
