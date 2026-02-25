from ..base_command import BaseCommand

class TimeCommand(BaseCommand):

    def __init__(self, basic_handler):
        self.basic_handler = basic_handler

    def matches(self, text: str) -> bool:
        return text.strip().lower() == "que horas são"

    def execute(self, text: str, context: dict) -> str:
        return self.basic_handler.ask_time()