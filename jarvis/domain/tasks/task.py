class Task:
    def __init__(self, title: str, id: int | None = None, completed: bool = False):
        self.id = id
        self.title = title
        self.completed = completed
        
    def complete(self):
        if self.completed:
            raise ValueError("Tarefa já está completa.")
        self.completed = True