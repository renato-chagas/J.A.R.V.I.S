import logging

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
            raise ValueError(f"Tarefa '{title}' não encontrada.")

        self.repository.delete(task.id)
        logging.info(f"Tarefa '{title}' deletada com sucesso.")
        
    def mark_task_complete_by_title(self, title: str):
        task = self.repository.find_by_title(title)

        if not task:
            raise ValueError(f"Tarefa '{title}' não encontrada.")

        task.complete()
        self.repository.update(task)
        logging.info(f"Tarefa '{title}' marcada como completa.")
        
    def rename_task_by_title(self, old_title: str, new_title: str):
        task = self.repository.find_by_title(old_title)

        if not task:
            raise ValueError(f"Tarefa '{old_title}' não encontrada.")

        task.title = new_title
        self.repository.update(task)
        logging.info(f"Tarefa '{old_title}' renomeada para '{new_title}' com sucesso.")
    
    def list_tasks(self):
        return self.repository.list_all()   
        logging.info("Lista de tarefas recuperada com sucesso.") 
    
        
        