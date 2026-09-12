# test_slack.py
from brain.connectors.slack import get_unread_mentions

channels = get_unread_mentions()
print(f"Found {len(channels)} channels:")
for c in channels:
    print(c.get("name"))