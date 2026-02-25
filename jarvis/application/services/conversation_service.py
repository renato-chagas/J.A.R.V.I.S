from jarvis.infrastructure.persistence.repositories.conversation_repository import ConversationRepository

class ConversationService:
    def __init__(self, repository):
        self.repository = repository
        
    def register(self, user_input: str, bot_response: str):
        
        if not user_input.strip():
            raise ValueError("O comando do usuario nao pode estar vazio!")
        
        self.repository.save(user_input, bot_response)
        
    def get_history(self):
        return self.repository.list_all()

