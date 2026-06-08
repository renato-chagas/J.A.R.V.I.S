import logging
from pathlib import Path
from difflib import SequenceMatcher

class ProjectScanner:
    """Radar de projetos inteligente com indexação e verificação de integridade Git."""
    
    def __init__(self, base_search_dirs: list = None):
        self.search_dirs = [Path(d).expanduser() for d in (base_search_dirs or ["~"])]
        self.ignore_dirs = {
            ".venv", "venv", "env", "node_modules", "__pycache__", "build", "dist", "out",
            ".cache", ".local", ".config", ".npm", ".vscode", ".git", "snap", "flatpak",
            "Downloads", "Pictures", "Videos", "Music", "bruno"
        }

    def _determine_project_type(self, path: Path) -> str:
        items = {x.name for x in path.iterdir()}
        if "manage.py" in items and "package.json" in items: return "fullstack_django_next"
        if "manage.py" in items: return "django_backend"
        if "package.json" in items: return "node_frontend"
        return "git_repo" if (path / ".git").exists() else "generic_code"

    def scan_for_project(self, project_name: str) -> dict:
        target = project_name.lower().strip()
        for search_dir in self.search_dirs:
            if not search_dir.exists(): continue
            
            # Walk otimizado
            for root, dirs, _ in os.walk(search_dir):
                dirs[:] = [d for d in dirs if d not in self.ignore_dirs]
                root_path = Path(root)
                folder_name = root_path.name.lower()
                
                score = SequenceMatcher(None, target, folder_name).ratio()
                if target == folder_name or score >= 0.85 or (target in folder_name and len(target) > 3):
                    if (root_path / ".git").exists() or any((root_path / m).exists() for m in ["package.json", "manage.py", "main.py"]):
                        return {
                            "path": str(root_path),
                            "type": self._determine_project_type(root_path),
                            "is_git": (root_path / ".git").exists()
                        }
        return None