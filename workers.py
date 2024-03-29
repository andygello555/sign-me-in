from datetime import datetime, timedelta
from utils.config import CONFIG
from utils.time_utils import get_pretty_range, get_pretty_time, get_utc_now, fromiso_Z
from registration import CannotLoginException, click_button
from time import sleep
import random
import threading
from utils.pipeline import Pipeline
from google_calendar import CalendarAPI
import pytz

# Gather parameters from config
MIN_CLICK_TIMEOUT = CONFIG.MIN_CLICK_TIMEOUT  # seconds
MAX_CLICK_TIMEOUT = CONFIG.MAX_CLICK_TIMEOUT  # seconds
STILL_ALIVE = CONFIG.STILL_ALIVE  # mins
BACKOFF_MULT = CONFIG.BACKOFF_MULT  # * seconds
LOOP_TIMEOUT = CONFIG.LOOP_TIMEOUT  # seconds

# The percentage of the way through that events will be scheduled to be signed into
SCHEDULE_START_PERCENT = CONFIG.SCHEDULE_START_PERCENT
SCHEDULE_END_PERCENT = CONFIG.SCHEDULE_END_PERCENT

HEADLESS = CONFIG.HEADLESS


def calendar_event_producer(info: list, calendar_api: CalendarAPI, pipeline: Pipeline, event: threading.Event):
    """
        Produces calendar events on the pipeline for every calendar.

        Flow:
        1. Check if one of the pipes is not full
        2. Get the event after the last event in the non-full pipe's relevant calendar
        3. Add that event to the queue

        Args:
            info: all chosen calendars to get events for
            calendar_api: interacts with the Google calendar API
            pipeline: pipeline to read/write to
            event: the exit event
    """

    # Get an event from a calendar to access the timezone
    timezone = pytz.timezone(calendar_api.get_next_n(info[0]['calendarId'])[0]['start']['timeZone'])
    
    # Construct a lookup table of the furthest events put into the queue, this means that the back of the 
    # queue doesn't need to be check
    furthest = {_info['calendarId']: get_utc_now(timezone, True) for _info in info}

    while not event.is_set():
        calendar_ID = pipeline.get_first_non_full()
        if calendar_ID is not None:
            calendar_info = list(filter(lambda x: x['calendarId'] == calendar_ID, info))[0]
            search_params = calendar_info['search_params']
            print(f'\nPRODUCER - Calendar: \"{calendar_info["calendarSummary"].upper()}\" has a non-full pipe')

            next_event = calendar_api.get_next_n(calendar_ID, after=furthest[calendar_ID], search_params=search_params)[0]
            furthest[calendar_ID] = next_event['end'].get('dateTime', next_event['end'].get('date', get_utc_now(timezone, True)))

            print(f'\tAdded event: \"{next_event["summary"]}\" ({get_pretty_range(next_event["start"]["dateTime"], next_event["end"]["dateTime"])})')
            pipeline.put_event(calendar_ID, next_event)
            if pipeline.full(calendar_ID):
                print(f'\t~ PIPE IS FULL ~')
        sleep(LOOP_TIMEOUT)

def button_consumer(info: dict, pipeline: Pipeline, event: threading.Event, selenium_lock: threading.Lock):
    """
        Consumes google calendar events and clicks the sign-in button.

        Each one will be assigned to a calendar to watch

        Flow:
        1. Check if there are events in the corresponding pipe's queue
        2. If so retrieve the event
        3. Wait until the event is going to happen + random_range(start, end - threshold) (while True + sleep())
        4. Use the click_button function to open web page and try and sign in
            4a. If this fails then keep retrying until the end of the event/success
        
        Args:
            info: the info of the calendar that the consumed events are coming from
            pipeline: pipeline object to read/write to
            event: the exit event
    """

    calendarId = info['calendarId']
    calendarSummary = info['calendarSummary']
    username = info['username']
    password = info['password']

    print(f'\n{calendarSummary.upper()} THREAD: Spinning up...')
    emergency_exit = False

    while not event.is_set() and not emergency_exit:
        if not pipeline.empty(calendarId):
            current_event = pipeline.get_event(calendarId)
            course_id = current_event['summary'].split(' ')[0].lower()

            start = fromiso_Z(current_event['start']['dateTime'])
            timezone = pytz.timezone(current_event['start']['timeZone'])
            start = start.astimezone(timezone)
            now = get_utc_now(timezone)

            # If we are midway through an event then the scheduled time will be somewhere between NOW and the end of the event
            # This shouldn't happen unless the bot is started during an event
            if now > start:
                start = now

            end = fromiso_Z(current_event['end']['dateTime'])
            end = end.astimezone(timezone)
            range_seconds = (end - start).seconds

            # This is the first time the register attendance page will be check, this is to stop botcheckers/checking when there isn't anything to check
            check_time = start + timedelta(seconds=random.randint(int(range_seconds * SCHEDULE_START_PERCENT), int(range_seconds * SCHEDULE_END_PERCENT)))
            check_time = check_time.replace(tzinfo=start.tzinfo)
            
            print(f'\n{calendarSummary.upper()} THREAD: Scheduled to sign into \"{current_event["summary"]}\" at {get_pretty_time(check_time)}')

            clicked = False
            # Keep looping until the check_time
            timeout = MIN_CLICK_TIMEOUT
            alive_message = True
            while not clicked and not event.is_set():
                now = get_utc_now(timezone)

                # Print a still alive message every STILL_ALIVE mins
                if now.minute % STILL_ALIVE == 0 and alive_message:
                    print(f'\n{calendarSummary.upper()} THREAD: STILL WAITING - UP NEXT: \"{current_event["summary"]}\" at {get_pretty_time(check_time)} - Time now: {get_pretty_time(now)}')
                    alive_message = False
                elif now.minute % STILL_ALIVE != 0:
                    alive_message = True

                if now >= end:
                    # Current time exceeds event time slot, so we should just discard this event and move onto the next
                    print(f'\n{calendarSummary.upper()} THREAD: Could not click on button within event time slot. Closing this event :(')
                    break
                elif now >= check_time:
                    try:
                        print(f'\n{calendarSummary.upper()} THREAD: Preparing to click-in... ', end='')

                        # Starting selenium so acquire lock, bad things could happen if another thread is scheduled during selenium
                        selenium_lock.acquire(blocking=True)
                        clicked = click_button(username, password, headless=HEADLESS, course_id=course_id, search_params=info['search_params'])
                        selenium_lock.release()

                        for_part = f'for \"{current_event["summary"]}\" at {get_pretty_range(current_event["start"]["dateTime"], current_event["end"]["dateTime"])}'
                        print(f'You have registered your attendance {for_part}' if clicked else f'Could not register attendance {for_part}, delaying by {timeout} seconds')

                        # If button has not been clicked then increase timeout
                        if not clicked:
                            timeout = int(timeout * BACKOFF_MULT)
                            if timeout > MAX_CLICK_TIMEOUT:
                                timeout = MAX_CLICK_TIMEOUT
                        else:
                            break
                    except CannotLoginException:
                        print(f'\n{calendarSummary.upper()} THREAD FATAL ERROR: Could not access account for \"{calendarSummary}\" as login info was incorrect. Terminating consumer...')
                        timeout = MIN_CLICK_TIMEOUT
                        emergency_exit = True
                        break
                sleep(timeout)
        sleep(LOOP_TIMEOUT)
