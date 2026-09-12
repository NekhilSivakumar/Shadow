import os
import requests
from fastapi import APIRouter
from shared.contracts import ActionResult
from brain.agent_loop import run_agent_step, start_new_task

router = APIRouter()

BODY_URL = os.getenv("BODY_URL", "http://localhost:8001")


@router.post("/observe")
def observe(result: ActionResult):
    return run_agent_step(result)


@router.post("/start-task")
def start_task(instruction: str):
    first_action = start_new_task(instruction)
    try:
        resp = requests.post(f"{BODY_URL}/execute", json=first_action.model_dump(), timeout=120)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"error": f"could not reach body: {e}", "first_action": first_action.model_dump()}