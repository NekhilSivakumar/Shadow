"""
Person A builds this file.

It should expose a small FastAPI (or Flask) service, separate from the
brain's service, that:

1. Receives an AgentAction (see shared/contracts.py) and executes it via
   PyAutoGUI / Windows UI Automation / AutoHotkey depending on action.type.
2. After executing, POSTs the resulting ActionResult back to the brain's
   /observe endpoint (default http://localhost:8000/observe).
3. Reports TwinStatus on a heartbeat/status endpoint.

Suggested port: 8001 (see shared/config.py CONTROL_LAYER_URL) — change in
both places if a different port is needed.

This stub is intentionally minimal so Person B's brain service can be
tested end-to-end before the real control layer exists.
"""

from fastapi import FastAPI

from shared.contracts import AgentAction, ActionResult

app = FastAPI(title="Digital Twin — Body (stub)")


@app.post("/execute", response_model=ActionResult)
def execute(action: AgentAction) -> ActionResult:
    # TODO(Person A): replace with real PyAutoGUI / UI Automation execution.
    print(f"[stub] would execute: {action}")
    return ActionResult(action_id=action.action_id, success=True, screenshot_b64=None)


@app.get("/health")
def health():
    return {"status": "body stub online"}
