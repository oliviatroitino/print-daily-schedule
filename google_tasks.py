import os
import datetime
import textwrap
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

load_dotenv()

scopes = os.getenv('TASKS_SCOPE', 'https://www.googleapis.com/auth/tasks').split(',')
task_id = os.getenv('TASK_ID')

def get_tasks_service():
    creds = None
    if os.path.exists('token_tasks.json'):
        creds = Credentials.from_authorized_user_file('token_tasks.json', scopes)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', scopes=scopes)
            creds = flow.run_local_server(port=0)
        with open('token_tasks.json', 'w') as token:
            token.write(creds.to_json())
    return build('tasks', 'v1', credentials=creds)

def list_tasklists(service):
    return service.tasklists().list().execute().get('items', [])

def get_tasks(service, tasklistId):
    tasks = service.tasks().list(tasklist=tasklistId).execute().get('items', [])
    return tasks

def collect_tasks(tasks):
    result = []
    if not tasks:
        result.append('No tasks found.')
    for task in tasks:
        title = task['title']
        if 'due' in task:
            due_str = task['due']
            due_dt = datetime.datetime.fromisoformat(due_str[:-1])
            prefix = due_dt.strftime('%Y-%m-%d %H:%M') + ' '
            indent = ' ' * len(prefix)
            available = int(os.getenv('WIDTH', '40')) - len(prefix)
            wrapped = textwrap.wrap(title, width=available, break_long_words=False)
            result.append(prefix + wrapped[0])
            for line in wrapped[1:]:
                result.append(indent + line)
        else:
            result.append(title)
    return result

