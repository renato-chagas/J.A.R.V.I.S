import os
import logging
from difflib import SequenceMatcher

class ProjectScanner:
    """O radar inteligente do J.A.R.V.I.S. com rastreio de atalhos e blindagem anti-loop."""
    
    def __init__(self, base_search_dirs: list = None):
        home_dir = os.path.expanduser("~")
        self.search_dirs = base_search_dirs or [home_dir]

    def _is_similar(self, hint_word: str, path_segment: str, threshold: float = 0.7) -> bool:
        hint = hint_word.lower().strip()
        seg = path_segment.lower().strip()
        if hint in seg or seg in hint: return True

        dictionary = {
            "documents": ["documentos", "docs"],
            "documentos": ["documents", "docs"],
            "projects": ["projetos", "programming", "dev"],
            "projetos": ["projects", "programming", "dev"],
            "personal": ["pessoais", "pessoal"],
        }
        if hint in dictionary:
            for eq in dictionary[hint]:
                if eq in seg or seg in eq: return True

        return SequenceMatcher(None, hint, seg).ratio() >= threshold

    def _determine_project_type(self, folder_contents: list) -> str:
        if ("manage.py" in folder_contents or "backend" in folder_contents) and ("package.json" in folder_contents or "frontend" in folder_contents):
            return "fullstack_django_next"
        elif "manage.py" in folder_contents:
            return "django_backend"
        elif "package.json" in folder_contents:
            return "node_frontend"
        return "generic_code"

    def _is_real_project(self, folder_contents: list, is_exact_match: bool) -> bool:
        if "bruno.json" in folder_contents:
            return False
        if is_exact_match:
            return True
        project_markers = {"package.json", "manage.py", ".git", "src", "backend", "frontend", "main.py"}
        return any(marker in folder_contents for marker in project_markers)

    def scan_for_project(self, project_name: str, path_hint: str = None) -> dict:
        project_name_lower = project_name.lower().strip()
        logging.info(f"Scanning for '{project_name}'...")
        
        ignore_dirs = {
            ".venv", "venv", "env", "node_modules", "__pycache__", "build", "dist", "out",
            ".cache", ".local", ".config", ".npm", ".mozilla", ".vscode", "snap", "flatpak",
            ".steam", "Steam", ".wine", "PlayOnLinux", ".var", 
            "Downloads", "Pictures", "Videos", "Music", "Imagens", "Vídeos", "Música",
            "bruno" 
        }

        hint_words = []
        if path_hint:
            clean_hint = path_hint.replace(',', ' ').replace('>', ' ').replace('/', ' ')
            hint_words = [word.strip().lower() for word in clean_hint.split() if word.strip()]

        visited_paths = set()

        for search_dir in self.search_dirs:
            if not os.path.exists(search_dir): continue
                
            for root, dirs, files in os.walk(search_dir, followlinks=True):
                real_path = os.path.realpath(root)
                if real_path in visited_paths:
                    dirs[:] = []
                    continue
                visited_paths.add(real_path)

                dirs[:] = [d for d in dirs if d not in ignore_dirs]
                
                path_segments = root.lower().split(os.sep)
                if hint_words:
                    match_sub_filtro = True
                    for word in hint_words:
                        if not any(self._is_similar(word, segment) for segment in path_segments):
                            match_sub_filtro = False
                            break
                    if not match_sub_filtro: continue 

                current_folder_name = os.path.basename(root).lower()
                is_exact = (project_name_lower == current_folder_name)
                is_fuzzy = SequenceMatcher(None, project_name_lower, current_folder_name).ratio() >= 0.8
                is_contained = (project_name_lower in current_folder_name and len(project_name_lower) >= 3)
                
                if is_exact or is_fuzzy or is_contained:
                    try:
                        tudo_na_pasta = os.listdir(root)
                    except PermissionError: continue
                    
                    if self._is_real_project(tudo_na_pasta, is_exact):
                        project_type = self._determine_project_type(tudo_na_pasta)
                        logging.info(f"Alvo localizado com sucesso: {root}")
                        return {"path": root, "type": project_type}
        return None