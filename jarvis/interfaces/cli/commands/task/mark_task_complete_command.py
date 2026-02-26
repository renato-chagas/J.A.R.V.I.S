from ..base_command import BaseCommand

class MarkTaskCompleteCommand(BaseCommand):
    def __init__(self, task_service ):
        self.task_service = task_service
        
    def matches(self, text: str) -> bool:
        return text.startswith("marcar tarefa ") and text.endswith(" completa")
    
    def execute(self, text: str, context: dict) -> str:
        print(f'{text[14:-9].strip()}')
        title = text[14:-9].strip()
    
        
        try:
            self.task_service.mark_task_complete_by_title(title)
            return f"Tarefa '{title}' marcada como completa."
        except ValueError as e:
            return str(e)