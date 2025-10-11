"""
title: Weather for Open WebUI
description: Give your AI access to the Weather from Open-Meteo!
git_url: https://gitlab.com/Ensorid/WeatherOWUI
author: Ensorid
author_url: https://gitlab.com/Ensorid
version: 0.0.1
license: MIT
"""

import requests
import logging
from pydantic import BaseModel, Field
from typing import Literal


logging.basicConfig(level=logging.INFO)


def get_city_location(city: str) -> tuple[float, float] | None:
    """
    Get the city (latitude, longitude) from his name with Open-Meteo geocoding API.
    :param city: The city name in ENGLISH to get the location from.
    :return: The city's latitude and longitude.
    """
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": city, "count": 1, "language": "en", "format": "json"}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        results = response.json()["results"]
        if not results:
            logging.warning(f"No results found for {city}")
            return None

        data = results[0]
        return data["latitude"], data["longitude"]

    except requests.RequestException as e:
        logging.error(f"Error during request : {e}")
        return None
    except KeyError as e:
        logging.error(f"No result for {city} : {e}")


weathercode_converter = {
    0: "Clear sky",
    1: "Mostly clear",
    2: "Partly cloudy",
    3: "Cloudy",
    45: "Foggy",
    48: "Rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Heavy drizzle",
    56: "Light freezing drizzle",
    57: "Heavy freezing drizzle",
    61: "Light rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Light snow",
    73: "Moderate snow",
    75: "Heavy snow",
    77: "Snow grains",
    80: "Light rain showers",
    81: "Moderate rain showers",
    82: "Heavy rain showers",
    85: "Light snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with light hail",
    99: "Thunderstorm with heavy hail",
}


class Tools:
    def __init__(self):
        """Initialize the Tool."""
        self.citation = True
        self.user_valves = self.UserValves()

    class UserValves(BaseModel):
        temperature_unit: Literal["celsius", "fahrenheit"] = Field(
            default="celsius",
            description="Temperature unit of the user's valves.",
        )

    def get_current_weather(self, city: str, __user__: dict = {}) -> str | None:
        """
        Get weather of a city from his geolocation
        :param city: The city name in ENGLISH to get the weather from.
        :return: The city's weather.
        """
        location = get_city_location(city)
        if not location:
            logging.warning(f"Weather location for '{city}' not found.")
            return None

        lat, long = location
        url = "https://api.open-meteo.com/v1/forecast"

        temperature_unit = __user__.get("valves", self.user_valves).temperature_unit

        params = {
            "latitude": lat,
            "longitude": long,
            "temperature_unit": temperature_unit,
            "current_weather": True,
            "timezone": "auto",
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            weather = data.get("current_weather")
            if not weather:
                logging.warning(f"No weather data for '{city}' was found.")
                return None

            temperature = weather.get("temperature")
            weathercode = weather.get("weathercode")

            weather_desc = weathercode_converter.get(weathercode)

            if weather_desc:
                weather_text = weather_desc.lower()
            else:
                weather_text = f"Unknown (code: {weathercode}). Please report this at https://github.com/Ensorid/WeatherOWUI/issues"

            return f"The weather at {city} is **{weather_text}**. The temperature is {temperature} {temperature_unit}. Make sure to translate everything right here to the user's language and only use {temperature_unit} as the temperature unit."

        except requests.RequestException as e:
            logging.error(f"Error during request : {e}")
            return None
