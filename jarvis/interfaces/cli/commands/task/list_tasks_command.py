from ..base_command import BaseCommand

class ListTasksCommand(BaseCommand):
    def __init__(self, task_service):
        self.task_service = task_service
        
    def matches(self, text: str) -> bool:
        return text.strip() == "listar tarefas"
        
    def execute(self, text: str, context: dict) -> str:
        tasks = self.task_service.list_tasks()
        if not tasks:
            return "Nenhuma tarefa encontrada."
        
        response = "Tarefas:\n"
        for task in tasks:
            status = "✅" if task.completed else "❌"
            response += f"{status} {task.title}\n"
        
        return response.strip()