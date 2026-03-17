import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import datetime
import subprocess
import requests
from pprint import pformat

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

SCHEDULE = "4380d16c4c569e8c92a27f6622e0bc869f5be9069c3d57a52cd13223d54fbf7c@group.calendar.google.com"
ROUTINE = "213a968c503a9037ddce3cf1616a93e441938da770ded218488f452cb37144d8@group.calendar.google.com"
SOCIAL = "2f4ccb4fab7b4c3c364986cb6cba03446cca89a4b8ce093a04eef4833c904e5e@group.calendar.google.com"
ASSIGNMENTS = "45e0e8464482acc2403e5a58064e2830991f82e642c757b432ab2173bc6f51bb@group.calendar.google.com"

debug_events = os.getenv('DEBUG_EVENTS', '').strip().lower() in {'1', 'true', 'yes', 'on'}


def get_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('calendar', 'v3', credentials=creds)

def getEvents(service, calendarId, time_min, time_max):
    events = service.events().list(
        calendarId=calendarId,
        timeMin=time_min,
        timeMax=time_max,
        singleEvents=True,
        orderBy='startTime'
    ).execute().get('items', [])

    return events

def collect_events(events, include_day=False):
    result = []
    if not events:
        result.append('No upcoming events found.')
    for event in events:
        start_str = event['start'].get('dateTime')
        if start_str:
            start_dt = datetime.datetime.fromisoformat(start_str)
            if include_day:
                result.append(start_dt.strftime('%H:%M') + ' ' + event['summary'] + ' (' + start_dt.strftime('%a %d-%m') + ')')
            else:
                result.append(start_dt.strftime('%H:%M') + ' ' + event['summary'])
        else:
            result.append('Hand in ' + event['summary'] + ' by today!!!')
    return result

def event_start_key(event):
    start = event['start'].get('dateTime', event['start'].get('date'))
    # Handle UTC suffix for fromisoformat compatibility.
    if isinstance(start, str) and start.endswith('Z'):
        start = start[:-1] + '+00:00'
    dt = datetime.datetime.fromisoformat(start)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    return dt.astimezone(datetime.timezone.utc)

def merge_and_sort_events(*event_lists):
    merged = []
    seen_ids = set()

    for events in event_lists:
        for event in events:
            start_str = event['start'].get('dateTime')
            if not start_str:
                continue  # Skip events without a valid start time
            if debug_events:
                print('\nEvent dictionary:\n' + pformat(event, sort_dicts=False, width=100))
            event_id = event.get('id')
            if event_id and event_id in seen_ids:
                continue
            if event_id:
                seen_ids.add(event_id)
            merged.append(event)

    same_start = {}
    for event in merged:
        key = event_start_key(event)
        same_start.setdefault(key, []).append(event)

    collisions = {k: v for k, v in same_start.items() if len(v) > 1}

    if debug_events:
        print("Collisions:\n" + pformat(collisions, sort_dicts=False, width=100))

    collapsed_events = []
    for start_key in sorted(same_start):
        events_at_start = same_start[start_key]
        if len(events_at_start) == 1:
            collapsed_events.append(events_at_start[0])
            continue

        merged_event = events_at_start[0].copy()
        summaries = []
        seen_summaries = set()
        for event in events_at_start:
            summary = event.get('summary', '').strip()
            if summary and summary not in seen_summaries:
                seen_summaries.add(summary)
                summaries.append(summary)
        merged_event['summary'] = ' / '.join(summaries)
        collapsed_events.append(merged_event)

    return collapsed_events


def send_to_printer(content: str):
    printer_name = os.getenv('PRINTER_NAME')
    if not printer_name:
        print('\n\nPRINTER_NAME is not set, skipping print.')
        return

    printer_name = printer_name.strip()
    subprocess.run(['lpr', '-P', printer_name], input=content, text=True, check=True)
    print(f'Sent to printer: {printer_name}')