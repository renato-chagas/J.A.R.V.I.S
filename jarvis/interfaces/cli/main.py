import os
import sqlite3
import time
from jarvis.infrastructure.engine.llm_client import LocalLLMClient
from jarvis.infrastructure.engine.main_control_loop import MainControlLoop

# Repositories
from jarvis.infrastructure.persistence.repositories import (
    TaskRepository,
    ConversationRepository,
    WorkspaceRepository,
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
from jarvis.interfaces.cli.commands.conversation.greeting_command import GreetingCommand
from jarvis.interfaces.cli.commands.conversation.time_command import TimeCommand
from jarvis.interfaces.cli.commands.conversation.cognitive_chat_command import (
    CognitiveChatCommand,
)

# Automation
from jarvis.infrastructure.automation import (
    SystemController,
    WorkspaceManager,
    SystemHealth,
    ProjectScanner,
    ScreenReader,
)
from jarvis.interfaces.cli.commands.automation import (
    OpenAppCommand,
    StartWorkspaceCommand,
    SystemHealthCommand,
)

# Audio
from jarvis.infrastructure.listener.listener import AudioListener

DB_PATH = os.path.join(os.path.dirname(__file__), "../../data/db/memory.db")


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

def main():
    init_db()

    # Domain & Services
    user = UserProfile("Tulipa")
    context = {"user": user}
    conversation_service = ConversationService(ConversationRepository(DB_PATH))
    task_service = TaskService(TaskRepository(DB_PATH))

    # Infrastructure
    llm_client = LocalLLMClient()
    sys_controller = SystemController()
    system_health = SystemHealth()
    scanner = ProjectScanner()
    workspace_manager = WorkspaceManager(
        sys_controller, WorkspaceRepository(DB_PATH), scanner
    )
    screen_reader = ScreenReader()
    listener = AudioListener()

    # Commands (Cognitive first so we can inject it into the control loop)
    cognitive_chat_cmd = CognitiveChatCommand(
        llm_client,
        conversation_service,
        system_health,
        sys_controller,
        workspace_manager,
        screen_reader,
    )

    # Initialize Control Loop AFTER dependencies are ready
    control_loop = MainControlLoop(cognitive_chat_cmd, screen_reader)

    basic_handler = BasicHandler()
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

    router = CommandRouter(commands, basic_handler)

    print(
        "J.A.R.V.I.S. nível 5 iniciado. Os sistemas periféricos estão online. Digite 'sair' para encerrar.\n"
    )

    while True:
        try:
            user_input = input(f"\n{user.name}: ")
            if user_input.lower() == "sair": break
            if user_input.lower() == "ouvir": 
                user_input = listener.ouvir() or ""
            
            if not user_input.strip(): continue

            response = control_loop.processar(user_input, context)
            if response is None:
                response = router.route(user_input, context)

            conversation_service.register(user_input, response)
            
            # Streaming
            print("J.A.R.V.I.S.: ", end="", flush=True)
            for char in str(response):
                print(char, end="", flush=True)
                time.sleep(0.01)
            print()

        except KeyboardInterrupt:
            break


if __name__ == "__main__":
    main()
