import os
import subprocess
import logging
import shutil
import sys
import psutil

from jarvis.infrastructure.voice.voice_engine import VoiceEngine

class WorkspaceManager:
    """Orquestrador autônomo e dinâmico multiplataforma."""

    def __init__(self, system_controller, workspace_repository, project_scanner):
        self.repo = workspace_repository
        self.scanner = project_scanner
        self.voice = VoiceEngine()
    
    def __init__(self, system_controller, workspace_repository, project_scanner):
        self.system_controller = system_controller
        self.repo = workspace_repository
        self.scanner = project_scanner

    def _get_terminal_cmd(self, working_dir, command):
        """Get terminal command arguments for opening a terminal in the given directory."""
        if sys.platform == "win32":
            return ["start", "cmd", "/c", f'cd /d "{working_dir}" && {command}']
        elif sys.platform == "darwin":
            script = f'tell application "Terminal" to do script "cd {working_dir} && {command}"'
            return ["osascript", "-e", script]
        else:
            terms = ["gnome-terminal", "konsole", "xfce4-terminal", "alacritty", "foot", "xterm"]
            term = next((t for t in terms if shutil.which(t)), "xterm")
            if term == "gnome-terminal":
                return [term, "--", "bash", "-c", f'cd "{working_dir}" && {command} ; exec bash']
            return [term, "-e", f'bash -c "cd {working_dir} && {command} ; exec bash"']

    def launch_workspace(self, workspace_name: str) -> str:
        name = workspace_name.lower().strip()
        project_data = self.repo.get_workspace(name)
        
        if not project_data:
            scan_result = self.scanner.scan_for_project(name)
            if not scan_result: raise FileNotFoundError(f"Projeto '{name}' não localizado.")
            project_data = scan_result
            self.repo.save_workspace(name, project_data["path"], project_data["type"])

        path, p_type = project_data["path"], project_data["type"]
        
        editor = "code" 
        if sys.platform == "win32": editor = "code.cmd"
        
        flags = []
        if sys.platform == "linux" and os.environ.get("XDG_SESSION_TYPE") == "wayland":
            flags = ["--ozone-platform=wayland", "--enable-features=WaylandWindowDecorations"]

        try:
            subprocess.Popen([editor] + flags + [path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self._execute_servers_by_type(path, p_type)
            return f"Ambiente '{name}' carregado em {path}."
        except Exception as e:
            return f"Erro ao iniciar workspace: {e}"
        
        msg = f"Environment '{workspace_name}' loaded."
        self.voice.speak(msg)
        return msg

    def _execute_servers_by_type(self, root_path: str, project_type: str):
        mapping = {
            "fullstack_django_next": [("backend", "pdm run python manage.py runserver"), ("frontend", "npm run dev")],
            "django_backend": [(root_path, "pdm run python manage.py runserver")],
            "node_frontend": [(root_path, "npm run dev")]
        }
        
        for p, cmd in mapping.get(project_type, []):
            d = os.path.join(root_path, p) if p != root_path else p
            if os.path.exists(d):
                subprocess.Popen(self._get_terminal_cmd(d, cmd), shell=(sys.platform == "win32"))

    def close_workspace(self, workspace_name: str) -> str:
        """Close workspace across platforms."""
        project_data = self.repo.get_workspace(workspace_name.lower().strip())
        if not project_data: return "Projeto não encontrado na memória."
        
        path = project_data["path"].lower()
        
        port_map = {"fullstack_django_next": [8000, 3000], "django_backend": [8000], "node_frontend": [3000]}
        target_ports = port_map.get(project_data["type"], [])
        
        for proc in psutil.process_iter(['pid']):
            try:
                for conn in proc.connections(kind='inet'):
                    if conn.laddr.port in target_ports:
                        proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied): continue
        
        msg = f"Shutdown sequence for '{workspace_name}' completed."
        self.voice.speak(msg) 
        return msg

        for proc in psutil.process_iter(['pid', 'cmdline', 'cwd']):
            try:
                cmdline = " ".join(proc.info['cmdline'] or []).lower()
                cwd = (proc.cwd() or "").lower()
                
                if ("code" in cmdline or "electron" in cmdline) and (path in cmdline or path in cwd):
                    parent = psutil.Process(proc.pid)
                    for child in parent.children(recursive=True):
                        child.kill()
                    parent.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied): continue
            
        if sys.platform == "linux":
            subprocess.run(["hyprctl", "dispatch", "closewindow", "address:active"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
        return f"Workspace '{workspace_name}' finalizado."

    def list_running_workspaces(self) -> str:
        """List running editor processes for debugging."""
        running = []
        for proc in psutil.process_iter(['pid', 'name', 'cwd', 'cmdline']):
            try:
                name = proc.info['name'].lower()
                if "code" in name or "electron" in name:
                    cwd = proc.cwd() or ""
                    cmdline = " ".join(proc.info['cmdline'] or "")
                    running.append(f"PID {proc.info['pid']}: CWD={cwd} | CMD={cmdline[:50]}...")
            except: continue
        return "\n".join(running) if running else "Nenhum editor rodando."