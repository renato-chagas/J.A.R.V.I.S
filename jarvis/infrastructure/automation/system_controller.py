import subprocess
import logging
import os
import platform

class SystemController:
    """Responsible for executing system-level actions and automation (Cross-platform)."""
    
    def __init__(self, workspace_path: str = None):
        self.workspace = workspace_path or os.path.expanduser("~")
        self.os_name = platform.system()

    def execute_command(self, command: str) -> str:
        """Executes a terminal command and returns the standard output."""
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                check=True, 
                text=True, 
                capture_output=True
            )
            logging.info(f"Command executed successfully: {command}")
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            error_msg = f"Failed to execute command '{command}'. Error output: {e.stderr.strip()}"
            logging.error(error_msg)
            raise RuntimeError(error_msg)

    def open_application(self, app_name: str) -> None:
        """Launches an application adapting to the current OS environment rules."""
        app_name_lower = app_name.lower()
        
        if self.os_name == "Windows":
            try:
                subprocess.Popen(
                    f"start {app_name}", 
                    shell=True, 
                    stdout=subprocess.DEVNULL, 
                    stderr=subprocess.DEVNULL
                )
                logging.info(f"Application invoked via CMD (Windows): {app_name}")
            except Exception as e:
                raise ValueError(f"Failed to launch '{app_name}' on Windows: {e}")
                
        elif self.os_name == "Linux":
            # Direct execution for Linux environments
            try:
                subprocess.Popen(
                    [app_name_lower], 
                    stdout=subprocess.DEVNULL, 
                    stderr=subprocess.DEVNULL
                )
                logging.info(f"Application invoked via Process (Linux): {app_name_lower}")
            except FileNotFoundError:
                raise ValueError(f"J.A.R.V.I.S. could not locate or execute '{app_name_lower}'.")