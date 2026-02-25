import sqlite3
import os

from jarvis.domain.tasks.task import Task

DB_PATH = os.path.join(os.path.dirname(__file__), "../../data/memory.db")

class TaskRepository:
    def __init__(self, db_path: str):
        self.db_path = db_path
        
    def _connect(self):
        return sqlite3.connect(self.db_path)
        
    def create(self, task: Task):
        with self._connect() as conn:
            curosor = conn.cursor()
            curosor.execute(
                "INSERT INTO tasks (title, completed) VALUES (?, ?)",
                (task.title, task.completed),
            )
            task.id = curosor.lastrowid

    def delete(self, task_id: int):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            
    def update(self, task: Task):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE tasks SET title = ?, completed = ? WHERE id = ?",
                (task.title, task.completed, task.id,)
            )
    
    def list_all(self):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, completed FROM tasks")
            list = cursor.fetchall()
            return [Task(id=row[0], title=row[1], completed=bool(row[2])) for row in list]
        
    def find_by_title(self, title: str):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, completed FROM tasks WHERE title = ?", (title,))
            row = cursor.fetchone()
            return Task(id=row[0], title=row[1], completed=bool(row[2])) if row else None
        
