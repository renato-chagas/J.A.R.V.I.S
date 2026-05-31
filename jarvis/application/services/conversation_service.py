import logging

from jarvis.infrastructure.persistence.repositories.conversation_repository import ConversationRepository

class ConversationService:
    def __init__(self, repository):
        self.repository = repository

    def register(self, user_input: str, bot_response: str) -> None:
        self.repository.add(user_input, bot_response)
        
    def get_recent_context(self, limit: int = 5) -> list:
        """Formats the raw DB rows into the JSON payload expected by the LLM."""
        raw_history = self.repository.get_recent_history(limit)
        formatted_history = []
        
        for user_msg, bot_msg in raw_history:
            formatted_history.append({"role": "user", "content": user_msg})
            formatted_history.append({"role": "assistant", "content": bot_msg})
            
        return formatted_history