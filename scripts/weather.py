import network
import urequests
import uasyncio

from datetime import datetime, timezone

import connection
from secrets import openweather_api_key

# Store weather data
class WeatherData:
    def __init__(self):
        self.temp = 0
        self.sunrise = datetime.now(timezone.utc)
        self.sunset = datetime.now(timezone.utc)


CONNECTION_TIMEOUT = 3


def get_data(city, units, lang):
    url = "https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units={units}&lang={lang}".format(city=city, api_key=openweather_api_key, units=units, lang=lang)
    res = urequests.post(url)
    return res.json()


async def get_temperature(data, frequency, loop=True):
    next_sleep = frequency
    # Run forever
    while loop:
        # Connect to wifi if not already connected
        retries = CONNECTION_TIMEOUT
        status = network.STAT_IDLE
        while retries > 0:
            status = await connection.connect()
            if status == network.STAT_GOT_IP:
                break;

        if status == network.STAT_GOT_IP:
            # Get the raw weather json data from openweathermap
            raw_data = get_data("Vancouver, CA", "metric", "en")

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
        
        if loop:
            await uasyncio.sleep(next_sleep)
