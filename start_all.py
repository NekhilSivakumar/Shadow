import subprocess
import time
import os

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
VENV_PYTHON = os.path.join(PROJECT_DIR, "venv", "Scripts", "python.exe")

print("Starting brain service...")
subprocess.Popen(
    f'cmd /k "cd /d "{PROJECT_DIR}" && "{VENV_PYTHON}" -m uvicorn brain.api.main:app --port 8000"',
    creationflags=subprocess.CREATE_NEW_CONSOLE,
)

time.sleep(3)

print("Starting body service...")
subprocess.Popen(
    f'cmd /k "cd /d "{PROJECT_DIR}" && "{VENV_PYTHON}" -m uvicorn body.control_layer:app --port 8001"',
    creationflags=subprocess.CREATE_NEW_CONSOLE,
)

print("Both services starting in separate windows.")