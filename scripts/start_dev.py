import subprocess
import platform
import os

os_name = platform.system()
print("Iniciando o ecossistema cognitivo do J.A.R.V.I.S...")

# 1. Resolve the absolute path to the project root and engine
base_dir = os.path.abspath(os.path.dirname(__file__))
root_dir = os.path.abspath(os.path.join(base_dir, ".."))
engine_dir = os.path.join(root_dir, "jarvis", "infrastructure", "engine", "core_cpp")

# 2. Launch the C++ server in the BACKGROUND (hidden)
if os_name == "Windows":
    # On Windows, use creation flags to hide the CMD window
    cmd_server = f'cd /d "{engine_dir}" && .\\build\\bin\\llama-server.exe -m models\\weights\\Qwen2.5-7B-Instruct-Q4_K_M.gguf --port 8080 -c 2048'
    # CREATE_NO_WINDOW = 0x08000000 prevents the black console window from opening
    subprocess.Popen(
        cmd_server, 
        shell=True, 
        creationflags=0x08000000,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
elif os_name == "Linux":
    # On Linux, run the command directly with Popen without invoking an x-terminal-emulator
    # Redirect outputs to DEVNULL so the process runs completely silently
    cmd_server = f'cd "{engine_dir}" && ./build/bin/llama-server -m models/weights/Qwen2.5-7B-Instruct-Q4_K_M.gguf --port 8080 -c 2048'
    subprocess.Popen(
        cmd_server, 
        shell=True, 
        stdout=subprocess.DEVNULL, 
        stderr=subprocess.DEVNULL
    )

print("[Motor] Servidor cognitivo inicializado em segundo plano na porta 8080.")

# 3. Start the J.A.R.V.I.S. CLI in the user's current terminal window
subprocess.run("pdm run cli", shell=True)