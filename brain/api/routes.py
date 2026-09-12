from fastapi import APIRouter
from shared.contracts import ActionResult
from brain.agent_loop import run_agent_step, start_new_task

router = APIRouter()


@router.post("/observe")
def observe(result: ActionResult):
    """Person A's control layer calls this after executing an action,
    handing back the result so the agent loop can decide the next step."""
    return run_agent_step(result)


@router.post("/start-task")
def start_task(instruction: str):
    """Kick off a new agent task, e.g. 'book my dentist appointment'."""
    return start_new_task(instruction)
from brain.memory.behavioral import get_behavior_profile, get_behavioral_arc

@router.get("/behavior-summary")
def behavior_summary():
    return {
        "profile": get_behavior_profile(),
        "arc": get_behavioral_arc(),
    }