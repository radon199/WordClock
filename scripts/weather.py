import network
import urequests
import time

from datetime import datetime, timezone

import connection
import neopixelarray
from secrets import openweather_api_key

# Store weather data
class WeatherData:
    def __init__(self):
        self.temp = 0
        self.sunrise = datetime.now(timezone.utc)
        self.sunset = datetime.now(timezone.utc)


CONNECTION_TIMEOUT = 3
WEATHER_TIMEOUT = 5


def get_data(city, units, lang):
    url = "https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units={units}&lang={lang}".format(city=city, api_key=openweather_api_key, units=units, lang=lang)
    res = urequests.post(url)
    return res.json()


def update_weather(data, data_lock):
    print("Updating weather...")
    neopixelarray.turn_on(*neopixelarray.WEATHER_INDEX, (255,255,0))
    # Connect to wifi if not already connected
    retries = CONNECTION_TIMEOUT
    status = network.STAT_IDLE
    while retries > 0:
        print("Connection timeout : "+str(retries))
        status = connection.connect()
        if status == network.STAT_GOT_IP:
            break
        retries -= 1
    time.sleep(1)

    if status == network.STAT_GOT_IP:
        # Get the raw weather json data from openweathermap
        raw_data = get_data("Vancouver, CA", "metric", "en")

        # aquire data lock
        data_lock.acquire()
        # Temperature data
        temp = raw_data.get("main", {}).get("temp", None)
        if temp:
            data.temp = float(temp)

        # Sunrise and sunset times
        sys = raw_data.get("sys", None)
        if sys:
            sunrise = sys.get("sunrise", None)
            sunset  = sys.get("sunset", None)
            if sunrise and sunset:
                data.sunrise = datetime.fromtimestamp(sunrise, timezone.utc)
                data.sunset  = datetime.fromtimestamp(sunset, timezone.utc)
        # release data lock
        data_lock.release()

        print("Weather data updated")
        neopixelarray.blink_once(*neopixelarray.WEATHER_INDEX, neopixelarray.GREEN, 100)
        return
    # Did not connect to network
    neopixelarray.blink(*neopixelarray.WEATHER_INDEX, neopixelarray.RED, 3, 50, 300)