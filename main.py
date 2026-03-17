import os
import textwrap
from dotenv import load_dotenv
import datetime

from google_calendar import get_service, getEvents, collect_events, merge_and_sort_events, send_to_printer
from weather import get_weather

load_dotenv()  # loads .env from current project folder

# Define .env variables
width = int(os.getenv("WIDTH", "40"))
div1 = (width-3)//2
div2 = width - div1 - 3
divider = ('-' * div1) + '=+=' + ('-' * div2)

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
''' DIVIDER VERSION: format divider-title-divider'''
def event_title(title, first_title=False, no_divider=False):
    if no_divider: result = []
    else:
        if first_title: result = [divider]
        else: result = ['\n' + divider]
    
    if len(title) > width:
        title_wrapped = textwrap.wrap(title, width=len(title)//1.5, break_long_words=False)
        for line in title_wrapped:
            result.append(line.center(width))
        if len(result[-1]) < width:
            result[-1] += '-' * (width - len(result[-1]))
        
        if not no_divider:
            result.append(divider + '\n')
    else:
        if no_divider:
            result.append(title.center(width))
        else:
            result.append(title.center(width) + '\n' + divider + '\n')

    return '\n'.join(result)

lines = []
lines.append(event_title(today.strftime('%d-%m-%Y'), True))
lines.append(event_title(f"Today's weather in {os.getenv('WEATHER_CITY', 'Madrid')}: {weather['temp']:.0f}\u00b0C, {weather['desc']}".center(len(divider)), True, True))

if today.isoweekday() in [6, 7]:  # Weekend
    lines.append("It's the weekend! No uni, just social events and preparation for the week.\n")
    lines.append(event_title("Social Schedule"))
    lines += collect_events(social_schedule)
    lines.append(event_title("Assignments for the Week"))
    lines += collect_events(assignments_week_schedule, include_day=True)
else: # Weekdays
    if today.isoweekday() not in [3]:  # Not Wednesday
        lines.append(event_title("Today's Uni Schedule + Assignments"))
        lines += collect_events(today_schedule)
    else: # Wednesday (no classes, only assignments)
        lines.append(event_title("Today's Assignments"))
        lines += collect_events(assignments_schedule)
        lines.append(event_title("Wednesday Routine"))
        lines += collect_events(wednesday_schedule)
    lines.append(event_title("Today's Social Schedule"))
    lines += collect_events(social_schedule)
    lines.append(event_title("Tomorrow's Schedule"))
    lines += collect_events(tomorrow_schedule)
    lines.append(event_title("Assignments for the Week"))
    lines += collect_events(assignments_week_schedule, include_day=True)
    lines.append("\n" + divider + "\n")

output = '\n'.join(lines)
print(output)
send_to_printer(output, save_as_txt=True) 

''' PRINT ALL CALENDARS '''
# for cal in service.calendarList().list().execute().get('items', []):
#     print(cal['id'], '-', cal['summary'])

''' # ALTERNATE TITLE VERSION: format no dividers, -= title =- '''
# def event_title(title):
#     result = ['']
#     title_line ='-= ' + title + ' =' + ('-' * (WIDTH - len(title) - 5)) + '\n'
#     if len(title_line) > WIDTH:
#         title_wrapped = textwrap.wrap(title_line, width=WIDTH, break_long_words=False)
#         for line in title_wrapped:
#             result.append(line)
#         if len(result[-1]) < WIDTH:
#             result[-1] += '-' * (WIDTH - len(result[-1]))
#     else:
#         result.append(title_line)
#     result.append('')

#     return '\n'.join(result)