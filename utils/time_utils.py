from datetime import datetime
from typing import Union

"""
    A collection of time utilities
"""

def get_utc_now(tz, iso: bool = False) -> Union[datetime, str]:
    """
        Gets the UTC time with the correct timezone.

        Args:
            tz: the timezone object
            iso: whether or not to return an a string in ISO format
        
        Returns:
            Datetime now if iso is false, otherwise a string in ISO format
    """
    now = datetime.now().astimezone(tz)
    return now if not iso else now.isoformat()

def get_pretty_time(t: datetime) -> str:
    """
        Short representation of a datetime, appropriate for lectures.

        Args:
            t: the time to format
        
        Returns:
            The formatted time as a string
    """
    
    return t.strftime('%a: %I:%M %p')

def get_pretty_range(t1, t2) -> str:
    """
        Short representation of a range of times.

        Args:
            t1: the time from, can be a datetime or a string IN ISO FORMAT
            t2: the time to, can be a datetime or a string IN ISO FORMAT
        
        Returns:
            The formatted time range as a string
    """

    if not isinstance(t1, datetime):
        t1 = fromiso_Z(t1)
    if not isinstance(t2, datetime):
        t2 = fromiso_Z(t2)
    
    return f'{get_pretty_time(t1)} - {t2.strftime("%I:%M %p")}'

def fromiso_Z(time: str) -> datetime:
    """
        Gives a datetime when given a string in ISO format.

        Will check and remove the Z inside the string as it cannot be parsed. I think google changed
        calendar API to use new Z type dateTimes

        Args:
            time: the datetime in ISO format

        Returns:
            The input ISO string as a datetime object 
    """
    return datetime.fromisoformat(time.replace('Z', ''))
