from ..base_command import BaseCommand


class AddTaskCommand(BaseCommand):

    def __init__(self, task_service):
        self.task_service = task_service

    def matches(self, text: str) -> bool:
        return text.startswith("tarefa ")

    def execute(self, text: str, context: dict) -> str:
        title = text[7:].strip()
        self.task_service.create_task(title)
        return f"Tarefa '{title}' adicionada com sucesso."