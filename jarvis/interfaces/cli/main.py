import os
import sqlite3

# Repositórios
from jarvis.infrastructure.persistence.repositories.task_repository import (
    TaskRepository,
)
from jarvis.infrastructure.persistence.repositories.conversation_repository import (
    ConversationRepository,
)

# Services
from jarvis.application.services.task_service import TaskService
from jarvis.application.services.conversation_service import ConversationService

# Domain
from jarvis.domain.user_profile import UserProfile
from jarvis.domain.personality import Personality

# Interface
from jarvis.interfaces.cli.handlers.basic_handler import BasicHandler
from jarvis.interfaces.cli.router import CommandRouter

# Commands
from jarvis.interfaces.cli.commands.task.add_task_command import AddTaskCommand
from jarvis.interfaces.cli.commands.task.remove_task_command import RemoveTaskCommand
from jarvis.interfaces.cli.commands.task.list_tasks_command import ListTasksCommand

from jarvis.interfaces.cli.commands.conversation.greeting_command import GreetingCommand
from jarvis.interfaces.cli.commands.conversation.time_command import TimeCommand


DB_PATH = os.path.join(os.path.dirname(__file__), "../../data/db/memory.db")


# =========================
# DATABASE INIT
# =========================
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_input TEXT NOT NULL,
            bot_response TEXT NOT NULL
        )
    """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            completed BOOLEAN NOT NULL DEFAULT 0
        )
    """
    )

    conn.commit()
    conn.close()


# =========================
# MAIN
# =========================
def main():
    init_db()

    # Domain
    user = UserProfile("Renato Chagas")
    personality = Personality("friendly")

    # Repositories
    task_repo = TaskRepository(DB_PATH)
    conversation_repo = ConversationRepository(DB_PATH)

    # Services
    task_service = TaskService(task_repo)
    conversation_service = ConversationService(conversation_repo)

    # Handlers
    basic_handler = BasicHandler()

    # Commands
    commands = [
        AddTaskCommand(task_service),
        RemoveTaskCommand(task_service),
        ListTasksCommand(task_service),
        GreetingCommand(basic_handler),
        TimeCommand(basic_handler),
    ]

    # Router
    router = CommandRouter(commands, basic_handler)

    print("J.A.R.V.I.S. nível 2 iniciado. Digite 'sair' para encerrar.\n")

    while True:
        user_input = input(f"{user.name}: ")

        if user_input.lower() == "sair":
            response = basic_handler.farewell()
            print(personality.respond(response))
            break

        if user_input.lower() == "lembrar":
            history = conversation_service.get_history()
            if not history:
                print(
                    personality.respond(
                        "Desculpe senhor, não há nada registrado na minha memória."
                    )
                )
            else:
                for h in history:
                    print(f"{h[0]}: Você: {h[1]} | J.A.R.V.I.S.: {h[2]}")
            continue

        response = router.route(user_input, {"user": user})

        print(personality.respond(response))
        conversation_service.register(user_input, response)


if __name__ == "__main__":
    main()
