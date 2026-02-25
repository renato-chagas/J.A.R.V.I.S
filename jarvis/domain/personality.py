class Personality:
    """Define a personalidade do J.A.R.V.I.S., estilo de resposta."""
    def __init__(self, style="friendly"):
        self.style = style
    
    def respond(self, message: str) -> str:
        if self.style == "friendly":
            return f"😎{message}"
        elif self.style == "formal":
            return f"[J.A.R.V.I.S.]: {message}"
        elif self.style == "sarcastic":
            return f"🙄 Oh, {message}... Que original."
        else:
            return message