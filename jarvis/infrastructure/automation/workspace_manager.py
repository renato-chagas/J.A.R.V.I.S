import subprocess, os, sys, shutil, psutil, logging
from jarvis.infrastructure.voice.voice_engine import VoiceEngine

class WorkspaceManager:
    def __init__(self, system_controller, workspace_repository, project_scanner):
        self.system_controller = system_controller
        self.repo = workspace_repository
        self.scanner = project_scanner
        self.voice = VoiceEngine()

    def launch_workspace(self, workspace_name: str) -> str:
        project_data = self.repo.get_workspace(workspace_name.lower().strip())
        if not project_data:
            scan = self.scanner.scan_for_project(workspace_name)
            if not scan: return f"Projeto '{workspace_name}' não encontrado."
            project_data = {"path": scan["path"], "type": scan["type"]}
            self.repo.save_workspace(workspace_name, project_data["path"], project_data["type"])

        path, p_type = project_data["path"], project_data["type"]
        self.system_controller.open_application("code", args=[path])
        self._execute_servers_by_type(path, p_type)
        
        msg = f"Ambiente {workspace_name} carregado."
        self.voice.speak(msg)
        return msg

    def _execute_servers_by_type(self, root_path, p_type):
        mapping = {
            "fullstack_django_next": [("backend", "pdm run python manage.py runserver"), ("frontend", "npm run dev")],
            "django_backend": [(root_path, "pdm run python manage.py runserver")],
            "node_frontend": [(root_path, "npm run dev")]
        }
        for p, cmd in mapping.get(p_type, []):
            d = os.path.join(root_path, p)
            if os.path.exists(d):
                cmd_list = ["gnome-terminal", "--", "bash", "-c", f'cd "{d}" && {cmd} ; exec bash']
                subprocess.Popen(cmd_list)

    def close_workspace(self, workspace_name: str) -> str:
        data = self.repo.get_workspace(workspace_name.lower().strip())
        if not data: return "Projeto não localizado."
        
        # Mata processos nas portas e o VS Code
        path = data["path"].lower()
        for proc in psutil.process_iter(['pid', 'cmdline', 'cwd']):
            try:
                cmd = " ".join(proc.info['cmdline'] or []).lower()
                cwd = (proc.cwd() or "").lower()
                if ("code" in cmd or "electron" in cmd) and (path in cmd or path in cwd):
                    proc.kill()
            except: continue
        return f"Workspace '{workspace_name}' encerrado."