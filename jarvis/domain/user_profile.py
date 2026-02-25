class UserProfile:
    """Armazena informações básicas do usuário."""
    
    def __init__(self, name: str):
        self.name = name
        self.preferences = {}
        
    def set_preference(self, key, str, value):
        """Define uma preferência do usuário."""
        self.preferences[key] = value
        
    def get_preference(self, key):
        """Retorna o valor de uma preferencia do usuario."""
        return self.preferences.get(key, None)
    
    