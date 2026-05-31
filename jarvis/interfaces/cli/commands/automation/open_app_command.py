import logging
from jarvis.interfaces.cli.commands.base_command import BaseCommand

class OpenAppCommand(BaseCommand):
    """Command to launch individual applications."""

    def __init__(self, system_controller):
        self.system_controller = system_controller

    def matches(self, text: str) -> bool:
        # Match phrases that start with "abrir " or "iniciar "
        return text.startswith("abrir ") or text.startswith("iniciar ")

    def execute(self, text: str, context: dict) -> str:
        # Extract the app name by removing the command prefix
        prefix = "abrir " if text.startswith("abrir ") else "iniciar "
        app_name = text[len(prefix):].strip()
        
        if not app_name:
            return "Qual aplicativo o senhor deseja que eu abra?"
            
        try:
            self.system_controller.open_application(app_name)
            return f"Comando aceito. Protocolo de inicialização para '{app_name}' ativado, senhor."
        except ValueError as e:
            return f"Sinto muito, senhor. {e}"
        except Exception as e:
            logging.error(f"Erro inesperado ao abrir app: {e}")
            return f"Ocorreu uma falha crítica ao tentar abrir o aplicativo: {e}"