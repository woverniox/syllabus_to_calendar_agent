import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Permissions: 'calendar' allows us to create/delete events
SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    # Pull from .env
    creds_data = {
        "token": os.getenv("GOOGLE_TOKEN"),
        "refresh_token": os.getenv("GOOGLE_REFRESH_TOKEN"),
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        "token_uri": "https://oauth2.googleapis.com/token",
    }

    # Initialize Credentials
    creds = Credentials.from_authorized_user_info(creds_data)

    # Refresh Credentials 
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

    return build('calendar', 'v3', credentials=creds)

def add_event_to_calendar(summary: str, date_str: str, description: str = ""):
    """
    Adds an all-day event to the primary Google Calendar.
    date_str must be in 'YYYY-MM-DD' format.
    """
    try:
        service = get_calendar_service()
        
        event = {
            'summary': summary,
            'description': description,
            'start': {
                'date': date_str,
                'timeZone': 'UTC',
            },
            'end': {
                'date': date_str,
                'timeZone': 'UTC',
            },
            'reminders': {
                'useDefault': True,
            },
        }

        created_event = service.events().insert(calendarId='primary', body=event).execute()
        return created_event.get('htmlLink')
        
    except Exception as e:
        print(f"Error creating calendar event: {e}")
        raise e
