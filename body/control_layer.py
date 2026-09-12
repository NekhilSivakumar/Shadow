import time
import base64
import subprocess
from io import BytesIO

import pyautogui
import requests
import os
from fastapi import FastAPI

from shared.contracts import AgentAction, ActionResult, ActionType

app = FastAPI(title="Digital Twin — Body (real, same-machine)")

pyautogui.FAILSAFE = True

BRAIN_URL = os.getenv("BRAIN_URL", "http://localhost:8000")
MAX_STEPS = 5


@app.post("/execute", response_model=ActionResult)
def execute(action: AgentAction) -> ActionResult:
    return _run_chain(action, steps_remaining=MAX_STEPS)


def _run_chain(action: AgentAction, steps_remaining: int) -> ActionResult:
    print(f"[real] executing (remaining={steps_remaining}): {action}")
    result = _perform_action(action)

    if steps_remaining <= 0:
        print("[real] step limit reached, stopping chain")
        return result

    try:
        resp = requests.post(f"{BRAIN_URL}/observe", json=result.model_dump(), timeout=120)
        resp.raise_for_status()
        next_action = AgentAction(**resp.json())
    except Exception as e:
        print(f"[real] chain stopped, could not reach brain: {e}")
        return result

    return _run_chain(next_action, steps_remaining=steps_remaining - 1)


def _perform_action(action: AgentAction) -> ActionResult:
    try:
        if action.type == ActionType.CLICK:
            pyautogui.click(x=action.x, y=action.y)
        elif action.type == ActionType.TYPE:
            pyautogui.write(action.text or "", interval=0.03)
        elif action.type == ActionType.SCROLL:
            pyautogui.scroll(-300)
        elif action.type == ActionType.KEY:
            pyautogui.press(action.key or "enter")
        elif action.type == ActionType.OPEN_APP:
            subprocess.Popen(f"start {action.app_name}", shell=True)
            time.sleep(2)
        elif action.type == ActionType.NAVIGATE_URL:
            subprocess.Popen(f"start {action.url}", shell=True)
            time.sleep(2)

        screenshot_b64 = _capture_screenshot()
        return ActionResult(action_id=action.action_id, success=True, screenshot_b64=screenshot_b64)

    except Exception as e:
        return ActionResult(action_id=action.action_id, success=False, error=str(e))


def _capture_screenshot() -> str | None:
    try:
        img = pyautogui.screenshot()
        buf = BytesIO()
        img.save(buf, format="JPEG", quality=50)
        return base64.b64encode(buf.getvalue()).decode()
    except Exception as e:
        print(f"[warning] screenshot capture failed: {e}")
        return None


@app.get("/health")
def health():
    return {"status": "body online (real, chained)"}