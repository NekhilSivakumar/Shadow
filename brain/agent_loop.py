import json
import os
import re
import time
import uuid

from dotenv import load_dotenv
load_dotenv()

import google.generativeai as genai

from shared.contracts import ActionResult, AgentAction, ActionType
from brain.connectors.notion import get_recent_pages
from brain.connectors.slack import get_unread_mentions
from brain.connectors.google import list_upcoming_events

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-3.6-flash")

_current_task = {"instruction": None, "history": [], "context": None, "plan": [], "plan_index": 0}


def start_new_task(instruction: str) -> AgentAction:
    _current_task["instruction"] = instruction
    _current_task["history"] = []
    _current_task["context"] = _gather_context(instruction)
    _current_task["plan"] = _build_plan(instruction)
    _current_task["plan_index"] = 0

    if _current_task["plan"]:
        return _next_plan_step()
    return _decide_next_action()


def run_agent_step(result: ActionResult) -> AgentAction:
    _current_task["history"].append(result.model_dump())

    if _current_task["plan_index"] < len(_current_task["plan"]):
        return _next_plan_step()

    return _decide_next_action()


def _next_plan_step() -> AgentAction:
    step = _current_task["plan"][_current_task["plan_index"]]
    _current_task["plan_index"] += 1
    print(f"[plan] step {_current_task['plan_index']}/{len(_current_task['plan'])}: {step}")
    return step


def _build_plan(instruction: str) -> list[AgentAction]:
    lower = instruction.lower()

    # Pattern: "open <app> and type <text>"
    match = re.search(r"open\s+([a-z0-9\-_ ]+?)\s+and\s+type\s+(.+)", lower)
    if match:
        app_name = match.group(1).strip()
        text = match.group(2).strip()
        return [
            AgentAction(action_id=str(uuid.uuid4()), type=ActionType.OPEN_APP, app_name=app_name),
            AgentAction(action_id=str(uuid.uuid4()), type=ActionType.TYPE, text=text),
            AgentAction(action_id=str(uuid.uuid4()), type=ActionType.SCREENSHOT),
        ]

    # Pattern: "check slack" / "check my slack"
    if re.search(r"check\s+(my\s+)?slack", lower):
        return [
            AgentAction(action_id=str(uuid.uuid4()), type=ActionType.OPEN_APP, app_name="slack"),
            AgentAction(action_id=str(uuid.uuid4()), type=ActionType.SCREENSHOT),
        ]

    # Pattern: "check notion" / "check my notion" / "open notion"
    if re.search(r"(check|open)\s+(my\s+)?notion", lower):
        return [
            AgentAction(action_id=str(uuid.uuid4()), type=ActionType.OPEN_APP, app_name="notion"),
            AgentAction(action_id=str(uuid.uuid4()), type=ActionType.SCREENSHOT),
        ]

    # Pattern: "check calendar" / "check my calendar"
    if re.search(r"check\s+(my\s+)?(google\s+)?calendar", lower):
        return [
            AgentAction(action_id=str(uuid.uuid4()), type=ActionType.NAVIGATE_URL, url="https://calendar.google.com"),
            AgentAction(action_id=str(uuid.uuid4()), type=ActionType.SCREENSHOT),
        ]

    # Pattern: "type <text>" (no app specified)
    match = re.search(r"^type\s+(.+)", lower.strip())
    if match:
        text = match.group(1).strip()
        return [
            AgentAction(action_id=str(uuid.uuid4()), type=ActionType.TYPE, text=text),
            AgentAction(action_id=str(uuid.uuid4()), type=ActionType.SCREENSHOT),
        ]

    # Pattern: "open <app>" only — single word, no "and"/multi-clause phrases
    match = re.search(r"^open\s+([a-z0-9\-_]+)$", lower.strip())
    if match:
        app_name = match.group(1).strip()
        return [
            AgentAction(action_id=str(uuid.uuid4()), type=ActionType.OPEN_APP, app_name=app_name),
        ]

    return []


def _gather_context(instruction: str) -> str:
    lower = instruction.lower()
    context_parts = []

    if "notion" in lower:
        try:
            pages = get_recent_pages()
            context_parts.append(f"Real Notion pages currently visible: {pages}")
        except Exception as e:
            context_parts.append(f"Notion lookup failed: {e}")

    if "slack" in lower:
        try:
            channels = get_unread_mentions()
            names = [c.get("name") for c in channels]
            context_parts.append(f"Real Slack channels currently visible: {names}")
        except Exception as e:
            context_parts.append(f"Slack lookup failed: {e}")

    if "calendar" in lower or "gmail" in lower or "email" in lower:
        try:
            events = list_upcoming_events()
            summaries = [e.get("summary") for e in events]
            context_parts.append(f"Real upcoming calendar events: {summaries}")
        except Exception as e:
            context_parts.append(f"Google Calendar lookup failed: {e}")

    return "\n".join(context_parts) if context_parts else "No connector data needed for this task."


def _decide_next_action() -> AgentAction:
    prompt = f"""You are controlling a computer to complete a task.
Task: {_current_task['instruction']}
Relevant real data: {_current_task['context']}
History so far: {_current_task['history']}

Respond with ONLY a JSON object, no other text, matching this shape:
{{"type": "click|type|scroll|key|screenshot|open_app|navigate_url", "x": int or null, "y": int or null, "text": string or null, "key": string or null, "url": string or null, "app_name": string or null}}
"""
    for attempt in range(3):
        try:
            response = model.generate_content(prompt)
            break
        except Exception as e:
            if "429" in str(e) or "ResourceExhausted" in str(e):
                print(f"[gemini] rate limited, waiting 30s (attempt {attempt+1}/3)")
                time.sleep(30)
            else:
                raise
    else:
        return AgentAction(action_id=str(uuid.uuid4()), type=ActionType.SCREENSHOT)

    raw = response.text.strip().strip("```json").strip("```").strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = {"type": "screenshot"}

    return AgentAction(
        action_id=str(uuid.uuid4()),
        type=ActionType(data.get("type", "screenshot")),
        x=data.get("x"),
        y=data.get("y"),
        text=data.get("text"),
        key=data.get("key"),
        url=data.get("url"),
        app_name=data.get("app_name"),
    )