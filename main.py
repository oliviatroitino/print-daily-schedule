import os
from dotenv import load_dotenv
import datetime

from google_calendar import get_service, getEvents, collect_events, merge_and_sort_events, send_to_printer
from weather import get_weather

load_dotenv()  # loads .env from current project folder
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY") 

if not WEATHER_API_KEY:
    raise ValueError("WEATHER_API_KEY is missing in .env")


# Define date and time range for today, tomorrow and the week
service = get_service()
today = datetime.date.today()
time_min = datetime.datetime(today.year, today.month, today.day, tzinfo=datetime.timezone.utc).isoformat()
time_max = datetime.datetime(today.year, today.month, today.day, 23, 59, 59, tzinfo=datetime.timezone.utc).isoformat()
time_min_tomorrow = datetime.datetime(today.year, today.month, today.day + 1, tzinfo=datetime.timezone.utc).isoformat()
time_max_tomorrow = datetime.datetime(today.year, today.month, today.day + 1, 23, 59, 59, tzinfo=datetime.timezone.utc).isoformat()
time_max_week = datetime.datetime(today.year, today.month, today.day + 7, 23, 59, 59, tzinfo=datetime.timezone.utc).isoformat()

# Get Google Calendar events for set time ranges
uni_schedule = getEvents(service, os.getenv("SCHEDULE"), time_min, time_max)
social_schedule = getEvents(service, os.getenv("SOCIAL"), time_min, time_max)
assignments_schedule = getEvents(service, os.getenv("ASSIGNMENTS"), time_min, time_max)
assignments_week_schedule = getEvents(service, os.getenv("ASSIGNMENTS"), time_min_tomorrow, time_max_week)
tomorrow_schedule = getEvents(service, os.getenv("SCHEDULE"), time_min_tomorrow, time_max_tomorrow)
today_schedule = merge_and_sort_events(uni_schedule, assignments_schedule)
wednesday_schedule = getEvents(service, os.getenv("ROUTINE"), time_min, time_max)

# Get Weather info for today
weather, err = get_weather(os.getenv("WEATHER_CITY", "Madrid"))

# Format output
lines = []
lines.append("----------------------=+=----------------------")
lines.append("\t\t   " + today.strftime('%d-%m-%Y'))
lines.append("----------------------=+=----------------------\n")
lines.append(f"Today's weather in {os.getenv('WEATHER_CITY', 'Madrid')}: {weather['temp']:.0f}\u00b0C, {weather['desc']}.")
lines.append("\n----------------------=+=----------------------\n")
if today.isoweekday() in [6, 7]:  # Weekend
    lines.append("It's the weekend! No uni schedule, just social events and assignments.\n")
    lines.append("----= Social Schedule =-----------------------\n")
    lines += collect_events(social_schedule)
    lines.append("\n----= Assignments for the Week =--------------\n")
    lines += collect_events(assignments_week_schedule, include_day=True)
else: # Weekdays
    if today.isoweekday() not in [3]:  # Not Wednesday
        lines.append("\n----= Today's Uni Schedule + Assignments =----\n")
        lines += collect_events(today_schedule)
    else: # Wednesday (no classes, only assignments)
        lines.append("\n----= Today's Assignments =-------------------\n")
        lines += collect_events(assignments_schedule)
        lines.append("\n----= Wednesday Routine =----------------------\n")
        lines += collect_events(wednesday_schedule)
    lines.append("\n----= Assignments for the Week =--------------\n")
    lines += collect_events(assignments_week_schedule, include_day=True)
    lines.append("\n----= Social Schedule =-----------------------\n")
    lines += collect_events(social_schedule)
    lines.append("\n----= Tomorrow's Schedule =-------------------\n")
    lines += collect_events(tomorrow_schedule)
    lines.append("\n----------------------=+=----------------------")

output = '\n'.join(lines)
print(output)
send_to_printer(output)

''' PRINT ALL CALENDARS '''
# for cal in service.calendarList().list().execute().get('items', []):
#     print(cal['id'], '-', cal['summary'])