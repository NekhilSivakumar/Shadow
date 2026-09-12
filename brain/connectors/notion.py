import os

from notion_client import Client

notion = Client(auth=os.getenv("NOTION_API_KEY"))


def get_recent_pages(limit: int = 5):
    results = notion.search(page_size=limit)
    return [r["id"] for r in results.get("results", [])]
