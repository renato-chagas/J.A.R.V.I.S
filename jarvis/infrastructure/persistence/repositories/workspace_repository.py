import sqlite3
import logging

class WorkspaceRepository:
    """Gerencia a persistência de caminhos e configurações de projetos conhecidos."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._initialize_table()

    def _initialize_table(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS workspaces (
                        name TEXT PRIMARY KEY,
                        absolute_path TEXT NOT NULL,
                        project_type TEXT NOT NULL
                    )
                    """
                )
                conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Failed to initialize workspaces table: {e}")

    def save_workspace(self, name: str, absolute_path: str, project_type: str) -> None:
        """Salva ou atualiza a localização de um projeto."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO workspaces (name, absolute_path, project_type) 
                    VALUES (?, ?, ?)
                    ON CONFLICT(name) DO UPDATE SET 
                        absolute_path=excluded.absolute_path,
                        project_type=excluded.project_type
                    """,
                    (name.lower(), absolute_path, project_type),
                )
                conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Failed to save workspace '{name}': {e}")

    def get_workspace(self, name: str) -> dict:
        """Recupera as informações de um projeto se o J.A.R.V.I.S. já o conhecer."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT absolute_path, project_type FROM workspaces WHERE name = ?", 
                    (name.lower(),)
                )
                row = cursor.fetchone()
                if row:
                    return {"path": row[0], "type": row[1]}
                return None
        except sqlite3.Error as e:
            logging.error(f"Failed to retrieve workspace '{name}': {e}")
            return None

    def delete_workspace(self, name: str) -> None:
        """Remove um projeto da memória para forçar um novo escaneamento na próxima tentativa."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM workspaces WHERE name = ?", 
                    (name.lower(),)
                )
                conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Falha ao deletar workspace '{name}': {e}")