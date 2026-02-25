from datetime import datetime

class BasicHandler:

    def greeting(self, user_name: str) -> str:
        return f"Olá, {user_name}! Como você está hoje?"

    def ask_time(self) -> str:
        now = datetime.now()
        return f"Agora são {now.strftime('%H:%M:%S')}."

    def farewell(self) -> str:
        return "Até mais, senhor!"

    def unknown_command(self) -> str:
        return "Desculpe, não entendi o comando."