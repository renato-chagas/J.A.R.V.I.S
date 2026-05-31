import sqlite3
import logging

class ConversationRepository:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def add(self, user_input: str, bot_response: str) -> None:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO conversations (user_input, bot_response) VALUES (?, ?)",
                    (user_input, bot_response),
                )
                conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Erro ao salvar conversa no banco: {e}")

    def get_recent_history(self, limit: int = 5) -> list:
        """
        Retrieve the most recent conversation pairs to build the LLM memory context.
        Returns them in chronological order (oldest first, newest last).
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT user_input, bot_response FROM conversations ORDER BY id DESC LIMIT ?",
                    (limit,)
                )
                rows = cursor.fetchall()
                rows.reverse()
                return rows
        except sqlite3.Error as e:
            logging.error(f"Erro ao buscar histórico: {e}")
            return []