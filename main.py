import threading
from time import sleep
from workers import button_consumer, calendar_event_producer
from utils.pipeline import Pipeline
from google_calendar import CalendarAPI
from utils import input_utils
import time
import concurrent.futures

info = []

try:
    # Initialise CalendarAPI, this will open browser and ask user to login into google account
    print('Browser might open asking to choose Google account to use with app. This is so that your uni calendar can be used to check when your timetabled lectures are.')
    time.sleep(3)
    calendar_api = CalendarAPI()

    # Choose calendars to keep track of
    calendar_api.choose_calendars()

    # Choose search params for each calendar
    print('\n\n\nEnter a list of comma seperated search paramters, for each calendar, that each google calendar event will be checked against to '
          'check for a sign-in button on the register attendance page. An empty list indicates a capture of all events.')
    for calendar in calendar_api.chosen_calendars:
        print(
            f'\n\nEnter seach params for calendar: {calendar[1]} (CASE INSENSITIVE)')
        info.append({
                    'calendarSummary': calendar[1],
                    'calendarId': calendar[2],
                    'search_params': [param.lower() for param in input_utils.handle_multiple_inputs('Enter a list of search params')]
                    })

        # Then ask the user for a username and password for campus connect
        info[-1]['username'], info[-1]['password'] = input_utils.handle_user_pass(
            'Please enter your Campus Connect login (same as Outlook login)')
    # print(info, calendar_api.chosen_calendars)

    # Then create the pipeline
    pipeline = Pipeline(info)

    event = threading.Event()
    print(f'\nStarting the {len(info)} worker bees to watch calendars (To quit: keyboard interrupt, e.g. CTRL+C. Quitting might take a while so be patient)\n')
    sleep(3)

    # Start threads
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(info) + 1) as executor:
        executor.submit(calendar_event_producer, info, calendar_api, pipeline, event)
        for calendar in info:
            executor.submit(button_consumer, calendar, pipeline, event)

        # Check for keyboard interrupts so that threads can exit safely
        while True:
            try:
                sleep(2)
            except KeyboardInterrupt:
                event.set()
            break
except RuntimeError as e:
    print(f'\n\nError: {e.args[0]}')
