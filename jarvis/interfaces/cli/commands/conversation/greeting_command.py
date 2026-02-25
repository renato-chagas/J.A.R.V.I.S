from ..base_command import BaseCommand


class GreetingCommand(BaseCommand):

    def __init__(self, basic_handler):
        self.basic_handler = basic_handler

    def matches(self, text: str) -> bool:
        return "ola" in text

    def execute(self, text: str, context: dict) -> str:
        user = context["user"]
        return self.basic_handler.greeting(user.name)