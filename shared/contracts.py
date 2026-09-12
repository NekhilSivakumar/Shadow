from pydantic import BaseModel
from typing import Optional
from enum import Enum


class ActionType(str, Enum):
    CLICK = "click"
    TYPE = "type"
    SCROLL = "scroll"
    KEY = "key"
    SCREENSHOT = "screenshot"
    OPEN_APP = "open_app"
    NAVIGATE_URL = "navigate_url"


class AgentAction(BaseModel):
    """Sent FROM the brain (Person B) TO the control layer (Person A)."""
    action_id: str
    type: ActionType
    x: Optional[int] = None
    y: Optional[int] = None
    text: Optional[str] = None
    key: Optional[str] = None
    url: Optional[str] = None
    app_name: Optional[str] = None


class ActionResult(BaseModel):
    """Sent FROM the control layer (Person A) BACK to the brain (Person B)."""
    action_id: str
    success: bool
    screenshot_b64: Optional[str] = None
    error: Optional[str] = None


class TwinStatus(BaseModel):
    """Heartbeat/state the control layer reports."""
    session_active: bool
    current_app: Optional[str] = None
    last_screenshot_b64: Optional[str] = None
