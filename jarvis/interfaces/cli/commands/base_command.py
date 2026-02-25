class BaseCommand:
    
    def matches(self, text:str) -> bool:
        raise NotImplementedError()
    
    def execute(self, text: str, context: dict) -> str:
        raise NotImplementedError()