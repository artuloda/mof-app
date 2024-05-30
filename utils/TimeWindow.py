from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

class TimeWindow:
    def __init__(self, start, end, time_zone, date_format="%d-%m-%Y %H:%M:%S"):
        """
        Initializes the time window with a start and end time.
        Args:
        - start (str): The start date/time as a string.
        - end (str): The end date/time as a string.
        - tz (str): The timezone identifier (e.g., 'Europe/Madrid').
        - date_format (str): The date/time format for start and end.
        """
        self.timezone = ZoneInfo(time_zone)
        self.date_format = date_format
        self.start = self.create_date(start)
        self.end = self.create_date(end)
        

    def create_date(self, date_str):
        """
        Parse the input string to create a datetime object with timezone
        Args:
        - date_str (str): The start date/time as a string.
        """
        return datetime.strptime(date_str,  self.date_format).replace(tzinfo=self.timezone)
    

    def set_tw_start(self, date_str):
        """
        Set the input string to create a datetime object with timezone as tw start
        Args:
        - date_str (str): The start date/time as a string.
        """
        self.start = self.create_date(date_str)


    def set_tw_end(self, date_str):
        """
        Set the input string to create a datetime object with timezone as tw end
        Args:
        - date_str (str): The end date/time as a string.
        """
        self.end = self.create_date(date_str)
    

    def shift(self, hours=0, minutes=0, seconds=0):
        """
        Shifts the time window by a specific amount of time.
        Args:
        - hours (int): Hours to shift.
        - minutes (int): Minutes to shift.
        - seconds (int): Seconds to shift.
        """
        delta = timedelta(hours=hours, minutes=minutes, seconds=seconds)
        self.start += delta
        self.end += delta
    

    def duration(self):
        """
        Returns the duration of the time window in minutes.
        """
        return (self.end - self.start).total_seconds() / 60
    

    def contains(self, time_to_check_str):
        """
        Checks if a specific point in time is within the time window.
        Args:
        - time_to_check_str (str): The date/time of the point to check as a string.
        """
        point_datetime = self.create_date(time_to_check_str)
        return self.start <= point_datetime <= self.end
    
    
    def __str__(self):
        """
        Returns a string representation of the time window.
        """
        return f"TWStart: {self.start.strftime(self.date_format)}, TWEnd: {self.end.strftime(self.date_format)}"
    