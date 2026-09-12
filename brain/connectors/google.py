"""
Gmail/Calendar connector.

For a hackathon timeline, use a simple OAuth "installed app" flow with a
locally cached token (google-auth-oauthlib), not a full web OAuth flow.

Steps:
1. Create OAuth client credentials in Google Cloud Console (Desktop app type).
2. Save the client secret JSON to the path in GOOGLE_CLIENT_SECRET_PATH (.env).
3. On first run, InstalledAppFlow will open a browser for consent and cache
   a token locally — subsequent runs reuse it.
"""

import os
from dotenv import load_dotenv
load_dotenv()

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/calendar.readonly",
]


def get_credentials():
    flow = InstalledAppFlow.from_client_secrets_file(
        os.getenv("GOOGLE_CLIENT_SECRET_PATH"), SCOPES
    )
    return flow.run_local_server(port=0)


def list_upcoming_events(max_results: int = 5):
    creds = get_credentials()
    service = build("calendar", "v3", credentials=creds)
    events_result = (
        service.events()
        .list(calendarId="primary", maxResults=max_results, singleEvents=True, orderBy="startTime")
        .execute()
    )
    return events_result.get("items", [])
