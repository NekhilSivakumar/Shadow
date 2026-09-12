import json
import os
import time

LOG_PATH = "data/episodic_log.jsonl"


def log_event(event: dict):
    os.makedirs("data", exist_ok=True)
    event["ts"] = time.time()
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(event) + "\n")


def recent_events(n: int = 20):
    if not os.path.exists(LOG_PATH):
        return []
    with open(LOG_PATH) as f:
        lines = f.readlines()[-n:]
    return [json.loads(line) for line in lines]
