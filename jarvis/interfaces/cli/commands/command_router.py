class CommandRouter:

    def __init__(self, commands):
        self.commands = commands

    def route(self, text: str, context: dict) -> str:
        text = text.lower().strip()

        for command in self.commands:
            if command.matches(text):
                return command.execute(text, context)

        return context["basic_handler"].unknown_command()