import logging
from jarvis.interfaces.cli.commands.base_command import BaseCommand

class StartWorkspaceCommand(BaseCommand):
    def __init__(self, workspace_manager):
        self.workspace_manager = workspace_manager

    def matches(self, text: str) -> bool:
        return "iniciar ambiente" in text.lower() or "abrir projeto" in text.lower()

    def execute(self, text: str, context: dict) -> str:
        # Pega a palavra após "abrir projeto" ou "iniciar ambiente"
        try:
            tokens = text.lower().replace("iniciar ambiente", "").replace("abrir projeto", "").split()
            if not tokens: return "Qual projeto, senhor?"
            return self.workspace_manager.launch_workspace(tokens[0])
        except Exception as e:
            logging.error(f"Erro no StartWorkspaceCommand: {e}")
            return "Falha ao montar o ambiente."