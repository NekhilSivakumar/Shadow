import os

from slack_sdk import WebClient

slack = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))


def get_unread_mentions():
    resp = slack.conversations_list()
    return resp["channels"]
