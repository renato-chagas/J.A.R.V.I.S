class Task:
    def __init__(self, id: int | None, title: str, completed: bool = False):
        self.id = id
        self.title = title
        self.completed = completed
        
    def complete(self):
        if self.completed:
            raise ValueError("Tarefa já está completa.")
        self.completed = True