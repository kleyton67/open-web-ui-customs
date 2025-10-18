from datetime import datetime


class Tools:
    def __init__(self):
        pass

    # Add your custom tools using pure Python code here, make sure to add type hints and descriptions

    def get_current_time(self) -> str:
        """
        Displays the current date and time.
        """

        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")  # Using 12-hour format with AM/PM
        current_date = now.strftime("%A, day %d, %B in the year %Y")  # Full weekday

        return f"Today is {current_date} in the ISO format, and the time now is {current_time}."
