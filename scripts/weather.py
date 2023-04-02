import network
import urequests
import uasyncio
from utils import get_local_time

from datetime import datetime, timezone

import connection
import neopixelarray
from secrets import openweather_api_key

CONNECTION_TIMEOUT = 3
WEATHER_TIMEOUT = 5
REQUEST_TIMEOUT = 10

# Conditions that are considered rain
RAIN_CONDITIONS = ["Rain", "Drizzle", "Thunderstorm"]


# Async loop
async def update_weather_loop(data):
    while True:
        update_weather(data)
        # Time in minutes to the next hour
        delay = ((60 - int(get_local_time().minute)) * 60)
        print("Next weather update in {} seconds".format(delay))
        await uasyncio.sleep(delay)


def get_data(city, units, lang):
    url = "https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units={units}&lang={lang}".format(city=city, api_key=openweather_api_key, units=units, lang=lang)
    res = urequests.post(url, timeout=REQUEST_TIMEOUT)
    return res.json()


def update_weather(data):
    print("Updating weather...")
    neopixelarray.turn_on(*neopixelarray.WEATHER_INDEX, neopixelarray.YELLOW)
    # Connect to wifi if not already connected
    status = connection.connect(CONNECTION_TIMEOUT)

    if status == network.STAT_GOT_IP:
        raw_data = {}
        # Get the raw weather json data from openweathermap
        for i in range(WEATHER_TIMEOUT):
            try:
                raw_data = get_data("Vancouver, CA", "metric", "en")
                break
            except:
                print("Unable to get weather.")
                neopixelarray.blink(*neopixelarray.CLOCK_INDEX, neopixelarray.RED, 3, 25, 100)

        # aquire data lock
        data.lock.acquire()
        # Temperature data
        temp = raw_data.get("main", {}).get("temp", None)
        if temp:
            data.temp = float(temp)

        # Weather condition
        condition = raw_data.get("weather", [])
        if condition:
            current_condition = condition[0].get("main", None)
            if current_condition:
                data.condition = current_condition

        # Sunrise and sunset times
        sys = raw_data.get("sys", None)
        if sys:
            sunrise = sys.get("sunrise", None)
            sunset  = sys.get("sunset", None)
            if sunrise and sunset:
                data.sunrise = datetime.fromtimestamp(sunrise, timezone.utc)
                data.sunset  = datetime.fromtimestamp(sunset, timezone.utc)
        # release data lock
        data.lock.release()

        print("Weather data updated")
        neopixelarray.blink_once(*neopixelarray.WEATHER_INDEX, neopixelarray.GREEN, 50)
        return
    # Did not connect to network
    neopixelarray.blink(*neopixelarray.WEATHER_INDEX, neopixelarray.RED, 3, 50, 200)