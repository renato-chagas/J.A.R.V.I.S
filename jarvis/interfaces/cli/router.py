class CommandRouter:

    def __init__(self, commands, basic_handler):
        self.commands = commands
        self.basic_handler = basic_handler

    def route(self, text: str, context: dict) -> str:
        text = text.lower().strip()

        for command in self.commands:
            if command.matches(text):
                return command.execute(text, context)

        return self.basic_handler.unknown_command()