from collections import Counter
import os

from dotenv import load_dotenv
load_dotenv()

import google.generativeai as genai

from brain.memory.episodic import recent_events

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
_model = genai.GenerativeModel("gemini-3.6-flash")


def get_behavior_profile(n: int = 50) -> dict:
    """Simple frequency-count profile over recent events."""
    events = recent_events(n)
    action_counts = Counter(e.get("type") for e in events if "type" in e)
    return {
        "total_events": len(events),
        "top_actions": action_counts.most_common(5),
    }


def get_behavioral_arc(n: int = 50) -> str:
    """Ask Gemini to summarize patterns in the real logged history.

    This does NOT train anything — it reads the actual logged events,
    turns them into plain text, and asks Gemini to describe trends fresh,
    the same way you'd ask it to summarize any other piece of text.
    """
    events = recent_events(n)

    if not events:
        return "No activity logged yet — nothing to summarize."

    log_lines = []
    for e in events:
        line = f"{e.get('type', 'unknown')}"
        if e.get("app_name"):
            line += f" ({e['app_name']})"
        if e.get("ts"):
            line += f" at ts={e['ts']:.0f}"
        log_lines.append(line)

    log_text = "\n".join(log_lines)

    prompt = f"""Here is a log of actions taken by a digital assistant, oldest first:

{log_text}

In 2-3 sentences, describe any patterns or behavioral trends you notice
(repeated actions, apps used most, anything that looks like a habit).
If there isn't enough variety to spot a real pattern yet, say so plainly
rather than inventing one."""

    response = _model.generate_content(prompt)
    return response.text.strip()