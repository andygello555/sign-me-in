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
    
    now = datetime.now().replace(tzinfo=tz)
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
        t1 = datetime.fromisoformat(t1)
    if not isinstance(t2, datetime):
        t2 = datetime.fromisoformat(t2)
    
    return f'{get_pretty_time(t1)} - {t2.strftime("%I:%M %p")}'
