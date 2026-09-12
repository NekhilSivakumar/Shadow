from collections import Counter

from brain.memory.episodic import recent_events


def get_behavior_profile(n: int = 50) -> dict:
    """Simple frequency-count profile over recent events.

    For a hackathon timeline this is intentionally simple: don't
    over-engineer it. Extend with real pattern-mining only if time remains.
    """
    events = recent_events(n)
    action_counts = Counter(e.get("type") for e in events if "type" in e)
    return {
        "total_events": len(events),
        "top_actions": action_counts.most_common(5),
    }
