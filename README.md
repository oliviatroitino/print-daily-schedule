# Print Daily Schedule

Small Python script that fetches Google Calendar events, adds weather, formats them for a receipt printer, and sends the result to CUPS (`lpr`).

## Features

- Reads events from multiple calendars
- Merges collisions with the same start time into one line
- Wraps long event titles to a fixed printer width
- Adds current weather (OpenWeather)
- Prints to a fixed printer queue (`PRINTER_NAME`)
- Optional debug output for raw event dictionaries
- Optional text snapshot output to `calendar.output.txt`

## Project Files

- `main.py`: Orchestrates date ranges, fetches data, formats output, and triggers print. This is the only file you should modify other than your .env.
- `google_calendar.py`: Google Calendar auth/fetching + merge/sort/print helpers
- `weather.py`: OpenWeather API call
- `.env.example`: template of required environment variables

## Requirements

- Python 3.10+
- macOS/Linux with CUPS (`lpstat`/`lpr` available)
- Google Calendar API credentials (`credentials.json`)
- OpenWeather API key

Install dependencies in your virtual environment:

```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib python-dotenv requests
```

## Setup

1. Copy environment template:

```bash
cp .env.example .env
```

2. Fill `.env` values:

- `WEATHER_API_KEY`: your [OpenWeather](https://home.openweathermap.org/api_keys) key 
- `SCHEDULE`: calendar ID (These can be acquired by un-commenting the PRINT ALL CALENDARS lines in main.py, they end in `@group.calendar.google.com`)
- `ROUTINE`: calendar ID
- `SOCIAL`: calendar ID
- `ASSIGNMENTS`: calendar ID
- `WEATHER_CITY`: city name (example: `Madrid`)
- `PRINTER_NAME`: exact CUPS printer queue name (To see your current printers, run `lpstat -p` on your terminal)
- `WIDTH`: printer text width in characters (example: `40`, 80mm printers are around 40-48 from my research)
- `DEBUG_EVENTS`: `true/false`

3. Google Credentials and API use:

    1. Create a project in [Google Cloud Console](https://console.cloud.google.com/).
    2. Create your OAuth 2.0 client (Desktop app) and download the credentials file, rename it and add it to your project directory as `credentials.json`.
    3. In API's and Services, add the Google Calendar API.
    4. First run will open browser auth and create `token.json`.

## Run

```bash
python main.py
```

If printing is enabled and `PRINTER_NAME` is set, output is sent to that printer queue.

Default code path in `main.py` calls:

```python
send_to_printer(output, save_as_txt=True)
```

So each run also writes `calendar.output.txt` for preview/debug.

## Formatting Notes (80mm printer)

- Use `WIDTH=40` as a safe default for most 80mm thermal printers.
- Long event names are wrapped in `collect_events()`.
- Divider and section titles are generated to match the configured width.

If lines still wrap incorrectly, reduce `WIDTH` to `38` or `36`.

## macOS Daily Automation (optional)

Use a LaunchAgent plist at:

`~/Library/LaunchAgents/com.[name].calendar.daily.plist`

Minimal command configuration:

- Python: `/path/to/project/env/bin/python`
- Script: `/path/to/project/main.py`
- WorkingDirectory: project root

Load/reload:

```bash
launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/com.olivia.calendar.daily.plist
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.olivia.calendar.daily.plist
```

## Troubleshooting

- `PRINTER_NAME is not set, skipping print.`
  - Set `PRINTER_NAME` in `.env`
  - Verify queue name with: `lpstat -p`

- Weather key errors
  - Ensure `WEATHER_API_KEY` is set and valid

- Google auth/token issues
  - Delete `token.json` and run again to re-authenticate

- Wrapped text still looks wrong
  - Adjust `WIDTH` value and test again

## Security

Do not commit secrets.

Keep these local only:

- `.env`
- `credentials.json`
- `token.json`
