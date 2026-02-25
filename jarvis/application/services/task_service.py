from jarvis.domain.tasks.task import Task

class TaskService:
    def __init__(self, repository):
        self.repository = repository

    def create_task(self, title:str):
        task = Task(id=None, title=title)
        self.repository.create(task)

        
    def delete_task_by_title(self, title: str):
        task = self.repository.find_by_title(title)

        if not task:
            raise ValueError("Tarefa não encontrada.")

        self.repository.delete(task.id)
    
    def complete_task(self, task_id: int):
        tasks = self.repository.list_all()
        task = next((t for t in tasks if t.id == task_id), None)
        
        if not task:
            raise ValueError("Tarefa não encontrada.")
        
        task.complete()
        self.repository.update(task)
    
    def list_tasks(self):
        return self.repository.list_all()    
    
        
        