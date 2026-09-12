import sys
import requests
import time
for name, url in [("brain", "http://localhost:8000/health"), ("body", "http://localhost:8001/health")]:
    try:
        requests.get(url, timeout=3)
    except Exception:
        print(f"ERROR: {name} service isn't running. Run start_all.bat first.")
        sys.exit(1)
if len(sys.argv) < 2:
    print("Usage: python run_task.py \"your instruction here\"")
    sys.exit(1)

instruction = " ".join(sys.argv[1:])
print(f"Running: {instruction}")

resp = requests.post(
    "http://localhost:8000/start-task",
    params={"instruction": instruction},
    timeout=180,
)
print("Result:", resp.json())