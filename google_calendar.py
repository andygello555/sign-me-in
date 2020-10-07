from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from tabulate import tabulate
from utils import input_utils

class NoCalendarsChosen(RuntimeError):
    """Raised when no calendars are chosen"""
    pass

class CalendarNotChosen(RuntimeError):
    """Raised when a calendar that is not chosen is queried"""
    pass

# If modifying these scopes, delete the file token.pickle.
class CalendarAPI:
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


    def __init__(self):
        """
            Basic implementation of the Google Calendar API as well as some helpful abstractions.

            Will cache all found calendars into an attribute
        """
        
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('calendar', 'v3', credentials=creds)

        self.calendars = self.service.calendarList().list().execute().get('items', [])
        self.calendars_short = [(i+1, calendar['summary'], calendar['id']) for i, calendar in enumerate(self.calendars)]
    
    def choose_calendars(self):
        """
            Interactive prompt which lets the user choose which calendars to keep track of

            Raises:
                NoCalendarChosen: when no calendar is chosen
        """
        print("Here are the calendars we found for your account:")
        print(tabulate(self.calendars_short), end='\n\n')
        
        calendarIds = input_utils.handle_multiple_range('Which calendar do you want to keep track of?', 'Are you sure?', ['y', 'n'], self.calendars_short)
        self.chosen_calendars = list(filter(lambda x: x[0] in calendarIds, self.calendars_short))
        
        if not len(self.chosen_calendars):
            raise NoCalendarsChosen('A calendar needs to be chosen')
        print('\nYou have chosen:')
        print(tabulate(self.chosen_calendars))
    
    def check_calendar_chosen(self, calendarId: str) -> bool:
        """
            This will just check the cached chosen calendars

            Args:
                calendarId: the calendar ID to check if chosen

            Returns:
                True if the calendar exists, otherwise false
        """
        return any([check[2] == calendarId for check in self.calendars_short])
    
    def get_next_n(self, calendarId: str, n: int = 1, after: str = None, search_params: list = None, cutoff: int = 30) -> list:
        """
            Get the next 'n' number of events in calendarId, after the time given

            Args:
                calendarId: the ID of the calendar to query
                n: the max number of events to return (default = 1)
                after: the time after which to query (if None then NOW), UTC + ISO format
                search_params: the list of search params to check the events against (None matches every event)
                cutoff: the number of total events to fetch from API. This is to stop infinte loops with the search params

            Raises:
                CalendarNotChosen: when the given calendarId is not present in the chosen calendars
            
            Returns:
                A list of the upcoming events conforming to the search params
        """

        # Check if the calendarId is valid
        if not self.check_calendar_chosen(calendarId):
            raise CalendarNotChosen(f'Calendar {calendarId} was not chosen and therefore cannot be queried')

        # Format the datetime to UTC
        now = datetime.datetime.utcnow().isoformat() + 'Z' if after is None else after

        events_result = self.service.events().list(calendarId=calendarId, timeMin=now,
                                    maxResults=cutoff, singleEvents=True,
                                    orderBy='startTime').execute()
        events = events_result.get('items', [])

        preened = []

        if search_params is not None:
            for event in events:
                if len(preened) < n:
                    for param in search_params:
                        if param in event['summary'].lower() or param in event['description'].lower():
                            preened.append(event)
                            break
                else:
                    break
        else:
            preened = events[:n]

        return preened


if __name__ == '__main__':
    api = CalendarAPI()
    api.choose_calendars()
    next_events = api.get_next_n(api.chosen_calendars[0][2], 4, search_params=['cs2800'])
    print(next_events, len(next_events))
