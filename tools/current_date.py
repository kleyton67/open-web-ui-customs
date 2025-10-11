import os
import requests
from datetime import datetime
from pydantic import BaseModel, Field


class Tools:
    def __init__(self):
        pass

    # Add your custom tools using pure Python code here, make sure to add type hints and descriptions

    def get_current_time(self) -> str:
        """
        Get the current time in a more human-readable format.
        """

        now = datetime.now()
        current_time = now.strftime("%I:%M:%S")
        current_date = now.strftime(
            "%A, %Y, %B %d"
        )  # Full weekday, month name, day, and year

        return f"Current Date and Time is  {current_date}, {current_time}"
