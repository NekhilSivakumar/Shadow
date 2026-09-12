import json
import os
import uuid

from dotenv import load_dotenv
load_dotenv()

import google.generativeai as genai

from shared.contracts import ActionResult, AgentAction, ActionType
from brain.connectors.notion import get_recent_pages
from brain.connectors.slack import get_unread_mentions

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-3.6-flash")

_current_task = {"instruction": None, "history": [], "context": None}


def start_new_task(instruction: str) -> AgentAction:
    _current_task["instruction"] = instruction
    _current_task["history"] = []
    _current_task["context"] = _gather_context(instruction)
    return _decide_next_action()


def run_agent_step(result: ActionResult) -> AgentAction:
    _current_task["history"].append(result.model_dump())
    return _decide_next_action()


def _gather_context(instruction: str) -> str:
    """Pull real data from connectors when the instruction references them,
    so Gemini reasons over actual state instead of guessing."""
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

    return "\n".join(context_parts) if context_parts else "No connector data needed for this task."


def _decide_next_action() -> AgentAction:
    prompt = f"""You are controlling a computer to complete a task.
Task: {_current_task['instruction']}
Relevant real data: {_current_task['context']}
History so far: {_current_task['history']}

Respond with ONLY a JSON object, no other text, matching this shape:
{{"type": "click|type|scroll|key|screenshot|open_app|navigate_url", "x": int or null, "y": int or null, "text": string or null, "key": string or null, "url": string or null, "app_name": string or null}}
"""
    response = model.generate_content(prompt)
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