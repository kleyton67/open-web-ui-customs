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
        current_time = now.strftime("%H:%M:%S")  # Using 12-hour format with AM/PM
        current_date = now.strftime("%A, %d, %B, %Y")  # Full weekday

        return f"Today is {current_date} in the ISO format, and the time now is {current_time}."
