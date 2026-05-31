import os
import sqlite3
from jarvis.infrastructure.engine.llm_client import LocalLLMClient

# Repositories
from jarvis.infrastructure.persistence.repositories import (
    TaskRepository,
    ConversationRepository,
    WorkspaceRepository
)

# Services
from jarvis.application.services.task_service import TaskService
from jarvis.application.services.conversation_service import ConversationService

# Domain
from jarvis.domain.user_profile import UserProfile

# Interface
from jarvis.interfaces.cli.handlers.basic_handler import BasicHandler
from jarvis.interfaces.cli.router import CommandRouter

# Commands
from jarvis.interfaces.cli.commands.task import (
    AddTaskCommand,
    RemoveTaskCommand,
    ListTasksCommand,
    MarkTaskCompleteCommand,
    ChangeTaskTitleCommand,
)

# Conversation commands
from jarvis.interfaces.cli.commands.conversation.greeting_command import GreetingCommand
from jarvis.interfaces.cli.commands.conversation.time_command import TimeCommand
from jarvis.interfaces.cli.commands.conversation.cognitive_chat_command import CognitiveChatCommand

# Automation controller
from jarvis.infrastructure.automation import (
    SystemController,
    WorkspaceManager,
    SystemHealth,
    ProjectScanner,
)

# automation commands
from jarvis.interfaces.cli.commands.automation import (
    OpenAppCommand,
    StartWorkspaceCommand,
    SystemHealthCommand,
)

# audio
from jarvis.infrastructure.listener.listener import AudioListener


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
    user = UserProfile("Tulipa") 
    context = {"user": user}

    # Repositories and services
    task_repo = TaskRepository(DB_PATH)
    conversation_repo = ConversationRepository(DB_PATH)
    task_service = TaskService(task_repo)
    conversation_service = ConversationService(conversation_repo)

    # Cognitive engine client
    llm_client = LocalLLMClient()

    # Controllers
    sys_controller = SystemController()
    system_health = SystemHealth()
    workspace_repo = WorkspaceRepository(DB_PATH)
    scanner = ProjectScanner()
    workspace_manager = WorkspaceManager(sys_controller, workspace_repo, scanner)

    # Handlers
    basic_handler = BasicHandler()

    # Commands
    cognitive_chat_cmd = CognitiveChatCommand(
        llm_client, conversation_service, system_health, sys_controller, workspace_manager
    )

    commands = [
        AddTaskCommand(task_service),
        ListTasksCommand(task_service),
        RemoveTaskCommand(task_service),
        MarkTaskCompleteCommand(task_service),
        ChangeTaskTitleCommand(task_service),
        GreetingCommand(basic_handler),
        TimeCommand(basic_handler),
        OpenAppCommand(sys_controller),
        StartWorkspaceCommand(workspace_manager),
        SystemHealthCommand(system_health),
        cognitive_chat_cmd,    
    ]

    # Router
    router = CommandRouter(commands, basic_handler)
    listener = AudioListener()

    print("J.A.R.V.I.S. nível 5 iniciado. Os sistemas periféricos estão online. Digite 'sair' para encerrar.\n")

    while True:
        user_input = input(f"{user.name}: ")

        if user_input.lower() == "sair":
            print(basic_handler.farewell())
            break

        if user_input.lower() == "ouvir":
            print("--- Escutando... ---")
            texto_capturado = listener.ouvir()
            if texto_capturado:
                print(f"Comando de voz: {texto_capturado}")
                response = cognitive_chat_cmd.execute(texto_capturado, context)
                print(response)
                conversation_service.register(texto_capturado, response)
            continue

        if user_input.lower() == "lembrar":
            continue

        response = router.route(user_input, context)
        print(response)
        conversation_service.register(user_input, response)

if __name__ == "__main__":
    main()