"""
Person A builds the REAL version of this file.

This stub simulates execution, logs each step to episodic memory,
and auto-chains with the brain's /observe endpoint.
"""

import os
import requests
from fastapi import FastAPI

from shared.contracts import AgentAction, ActionResult
from brain.memory.episodic import log_event

app = FastAPI(title="Digital Twin — Body (stub)")

BRAIN_URL = os.getenv("BRAIN_URL", "http://localhost:8000")
MAX_STEPS = 5


@app.post("/execute", response_model=ActionResult)
def execute(action: AgentAction) -> ActionResult:
    return _run_chain(action, steps_remaining=MAX_STEPS)


def _run_chain(action: AgentAction, steps_remaining: int) -> ActionResult:
    print(f"[stub] executing step (remaining={steps_remaining}): {action}")

    log_event({
        "action_id": action.action_id,
        "type": action.type.value,
        "app_name": action.app_name,
        "url": action.url,
    })

    result = ActionResult(action_id=action.action_id, success=True, screenshot_b64=None)

    if steps_remaining <= 0:
        print("[stub] step limit reached, stopping chain")
        return result

    try:
        resp = requests.post(f"{BRAIN_URL}/observe", json=result.model_dump(), timeout=10)
        resp.raise_for_status()
        next_action = AgentAction(**resp.json())
    except Exception as e:
        print(f"[stub] chain stopped, could not reach brain: {e}")
        return result

    return _run_chain(next_action, steps_remaining=steps_remaining - 1)


@app.get("/health")
def health():
    return {"status": "body stub online"}