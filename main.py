import json
import threading
from time import sleep

from googleapiclient.errors import HttpError
from utils.file import IncorrectPassword, calendars_exists, load_latest_calendar, save_encrypted
from workers import button_consumer, calendar_event_producer
from utils.pipeline import Pipeline
from google_calendar import CalendarAPI
from utils import input_utils
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys
import traceback

info = []

try:
    # Initialise CalendarAPI, this will open browser and ask user to login into google account
    print('Browser might open asking to choose Google account to use with app. This is so that your uni calendar can be used to check when your timetabled lectures are.')
    time.sleep(2)
    calendar_api = CalendarAPI()

    simple_input_mode = False
    if len(sys.argv) - 1:
        # If the simple command line option is given then assume that most recent calendar info 
        # file should be used and use a normal input for password entry
        if len(sys.argv) == 2 and sys.argv[1] == '--simple':
            print('~ Continuing using simple input mode ~')
            simple_input_mode = True
        else:
            print('Unrecognized command line arguments')

    auto = False
    # If there exists a recent calendar info file then ask user if they want to decrypt and use it
    if calendars_exists():
        if simple_input_mode or input_utils.ask_for('Do you want to use the most recently saved calendar info file (requires password for decryption)?', input_utils.Y_OR_N):
            while True:
                try:
                    info = load_latest_calendar(simple=simple_input_mode)
                    auto = True
                    # Assign the chosen calendars in the api instance
                    calendar_api.chosen_calendars = [(next(filter(lambda c: c[2] == calendar['calendarId'], calendar_api.calendars_short))[0], calendar['calendarSummary'], calendar['calendarId']) for calendar in info]
                    break
                except IncorrectPassword as e:
                    if not simple_input_mode:
                        print(e)
                        if not input_utils.ask_for('Do you want to try again?', input_utils.Y_OR_N):
                            break
                    else:
                        raise RuntimeError(e)

    if not auto:
        # Choose calendars to keep track of if not found from a recent calendar file
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
        # print(f'Info:\n{json.dumps(info, indent=4, sort_keys=True)}\n\nChosen:\n{calendar_api.chosen_calendars}')

        # Ask if user wants to save calendar info to an encrypted file
        if input_utils.ask_for('Do you want to save this info to an encrypted file so that the bot can be started quicker next time?', input_utils.Y_OR_N):
            save_encrypted(info)

    # Then create the pipeline
    pipeline = Pipeline(info)

    event = threading.Event()
    selenium_lock = threading.Lock()
    print(f'\nStarting the {len(info)} worker bees to watch calendars (To quit: keyboard interrupt, e.g. CTRL+C. Quitting might take a while so be patient)\n')
    sleep(3)

    # Start threads
    futures = []
    with ThreadPoolExecutor(max_workers=len(info) + 1) as executor:
        futures.append(executor.submit(calendar_event_producer, info, calendar_api, pipeline, event))
        for calendar in info:
            futures.append(executor.submit(button_consumer, calendar, pipeline, event, selenium_lock))

        for future in as_completed(futures):
            try:
                future.result()
            except Exception as exc:
                print(exc)
                traceback.print_tb(exc.__traceback__)

        # Check for keyboard interrupts so that threads can exit safely
        while True:
            try:
                sleep(2)
            except KeyboardInterrupt:
                event.set()
            break
except RuntimeError as e:
    print(f'\n\nError: {e.args[0]}')
