class UserProfile:
    """Stores basic user profile information."""
    
    def __init__(self, name: str):
        self.name = name
        self.preferences = {}
        
    def set_preference(self, key: str, value):
        """Sets a user preference value."""
        self.preferences[key] = value
        
    def get_preference(self, key):
        """Returns a user preference value."""
        return self.preferences.get(key, None)
    
    