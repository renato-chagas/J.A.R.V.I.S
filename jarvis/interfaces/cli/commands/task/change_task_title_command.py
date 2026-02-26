from ..base_command import BaseCommand

class ChangeTaskTitleCommand(BaseCommand):
    def __init__(self, task_service):
        self.task_service = task_service
        
    def matches(self, text: str) -> bool:
        return text.startswith("renomear tarefa ") and " para " in text
    
    def execute(self, text: str, context: dict) -> str:
        parts = text[16:].split(" para ")
        if len(parts) != 2:
            return "Formato inválido. Use: renomear tarefa <título antigo> para <título novo>"
        
        old_title = parts[0].strip()
        new_title = parts[1].strip()
        
        try:
            self.task_service.rename_task_by_title(old_title, new_title)
            return f"Tarefa '{old_title}' renomeada para '{new_title}'."
        except ValueError as e:
            return str(e)