import logging
from jarvis.interfaces.cli.commands.base_command import BaseCommand

class StartWorkspaceCommand(BaseCommand):
    """Command to launch full workspace environments."""

    def __init__(self, workspace_manager):
        self.workspace_manager = workspace_manager

    def matches(self, text: str) -> bool:
        # Match triggers like "ambiente dev", "iniciar ambiente dev", etc.
        return "ambiente " in text

    def execute(self, text: str, context: dict) -> str:
        # Extract the token that comes right after "ambiente "
        parts = text.split("ambiente ")
        if len(parts) > 1 and parts[1].strip():
            workspace_name = parts[1].strip().split()[0] # Keep only the first word of the workspace name
        else:
            return "Por favor, especifique o nome do ambiente, senhor."
            
        try:
            result = self.workspace_manager.launch_workspace(workspace_name)
            return result
        except ValueError as e:
            return str(e)
        except Exception as e:
            logging.error(f"Erro ao iniciar workspace: {e}")
            return f"Senhor, os sistemas relataram uma falha ao montar o ambiente '{workspace_name}'. Detalhes nos logs."