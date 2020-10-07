from typing import Union
from queue import Empty, Queue

class Pipeline():
    """
        Manages the pipeline of google calendar events

        Attributes:
            pipes: a dictionary containing the queues of calendar events for all watched calendars 
    """

    class NonExistantCalendarPipe(KeyError):
        """Raised when a given calendar ID does not exist in the pipeline"""
        pass

    def __init__(self, info: list, max_stored: int = 3):
        """
            Constructs a new pipeline

            Args:
                info: the list containing the calendar info
                max_stored: the maximum number of events that a pipe can hold
            
            Returns:
                Pipeline instance
        """
        # Stores the queue for each calendar being watched as well as the calendar
        # summaries and ID
        self.pipes = {calendar['calendarId']: Queue(max_stored) for calendar in info}
    
    def _check_exists(self, calendarId: str):
        """
            Checks if the calendar of the given ID exists in the pipeline

            Args:
                calendarId: the calendar ID to check
            
            Raises:
                NonExistantCalendarPipe: if the calendar of the given ID does not exist inside the pipeline
        """
        if calendarId not in self.pipes:
            raise self.NonExistantCalendarPipe
    
    def _check_empty(self, calendarId: str):
        """
            Checks if the pipe corresponding to the given calender ID is empty

            Raises:
                Empty if the queue is empty
        """

        if self.pipes[calendarId].empty():
            raise Empty()
    
    def get_first_non_full(self) -> Union[str, None]:
        """
            Gets the first non-full queue

            Returns:
                A calendarId related to the first non-full queue, otherwise None
        """

        for id in self.pipes.keys():
            if not self.pipes[id].full():
                return id
        return None
    
    def put_event(self, calendarId: str, event) -> bool:
        """
            Puts an event into the appropriate pipe queue

            Args:
                calendarId: the calendar that is related to the event
                event: the event to add
            
            Raises:
                NonExistantCalendarPipe: if the given calendarId does not have a correlated pipe
            
            Returns:
                True if added, False if full
        """

        self._check_exists(calendarId)
        if not self.pipes[calendarId].full():
            self.pipes[calendarId].put(event)
            return True
        return False
    
    def get_event(self, calendarId: str):
        """
            Gets the next event from the appropriate pipe queue

            Args:
                calendarId: the calendar that is related to the pipe to get from
            
            Raises:
                NonExistantCalendarPipe: if the given calendarId does not have a correlated pipe
            
            Returns:
                The event if no problems occured, otherwise None
        """

        self._check_exists(calendarId)
        if not self.pipes[calendarId].empty():
            return self.pipes[calendarId].get()
        return None
    
    def empty(self, calendarId: str) -> bool:
        """
            Checks if the queue related to the given calendar ID is empty

            Args:
                calendarId: the calendar that is related to the pipe to check
            
            Returns:
                True if empty, False otherwise
        """

        self._check_exists(calendarId)
        return self.pipes[calendarId].empty()
    
    def full(self, calendarId: str) -> bool:
        """
            Checks if the queue related to the given calendar ID is full

            Args:
                calendarId: the calendar that is related to the pipe to check
            
            Returns:
                True if full, False otherwise
        """

        self._check_exists(calendarId)
        return self.pipes[calendarId].full()
    
    def front(self, calendarId: str) -> dict:
        """
            Returns the front of the queue without removing it

            Args:
                calendarId: the calendar that is related to the pipe to check
            
            Returns:
                The event at the front of the queue
        """

        self._check_exists(calendarId)
        self._check_empty(calendarId)
        return self.pipes[calendarId].queue[0]
    
    def back(self, calendarId: str) -> dict:
        """
            Returns the front of the queue without removing it

            Args:
                calendarId: the calendar that is related to the pipe to check
            
            Returns:
                The event at the front of the queue
        """

        self._check_exists(calendarId)
        self._check_empty(calendarId)
        return self.pipes[calendarId].queue[-1]
