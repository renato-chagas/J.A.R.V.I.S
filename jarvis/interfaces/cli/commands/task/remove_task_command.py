from ..base_command import BaseCommand

class RemoveTaskCommand(BaseCommand):
    def __init__(self, task_service):
        self.task_service = task_service
        
    def matches(self, text: str) -> bool:
        return text.startswith("remover tarefa ")
        
    def execute(self, text: str, context: dict) -> str:
        title = text[15:].strip()

        try:
            self.task_service.delete_task_by_title(title)
            return f"Tarefa '{title}' removida com sucesso."
        except ValueError as e:
            return str(e)