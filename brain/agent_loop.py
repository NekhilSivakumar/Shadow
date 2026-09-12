import uuid

import anthropic

from shared.config import ANTHROPIC_API_KEY
from shared.contracts import ActionResult, AgentAction, ActionType

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# Simple in-memory task state for the hackathon — replace with memory/episodic.py later.
_current_task = {"instruction": None, "history": []}


def start_new_task(instruction: str) -> AgentAction:
    _current_task["instruction"] = instruction
    _current_task["history"] = []
    return _decide_next_action()


def run_agent_step(result: ActionResult) -> AgentAction:
    _current_task["history"].append(result.model_dump())
    return _decide_next_action()


def _decide_next_action() -> AgentAction:
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        tools=[
            {
                "type": "computer_20250124",
                "name": "computer",
                "display_width_px": 1280,
                "display_height_px": 800,
            }
        ],
        messages=[
            {
                "role": "user",
                "content": (
                    f"Task: {_current_task['instruction']}\n"
                    f"History so far: {_current_task['history']}"
                ),
            }
        ],
    )

    for block in response.content:
        if block.type == "tool_use":
            action_input = block.input
            coordinate = action_input.get("coordinate", [None, None])
            return AgentAction(
                action_id=str(uuid.uuid4()),
                type=ActionType(action_input.get("action", "screenshot")),
                x=coordinate[0],
                y=coordinate[1],
                text=action_input.get("text"),
            )

    return AgentAction(action_id=str(uuid.uuid4()), type=ActionType.SCREENSHOT)
