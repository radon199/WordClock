import _thread
import time

import neopixelarray
import clock
import ntpsync
import weather

# Update weather and time once an hour
WEATHER_UPDATE = 3600

# Global variable, hold the weather data
WEATHER_DATA = weather.WeatherData()

# Weather and time lock
LOCK = _thread.allocate_lock()

print("Initalization...")
neopixelarray.bootup_check()
ntpsync.sync_time(LOCK)
weather.update_weather(WEATHER_DATA, LOCK)
print("Initalization complete")

def background_thread():
    # update_face will run forever
    clock.update_face(WEATHER_DATA, LOCK)

def main_thread():
    # Run forever. Sync time and update weather need to run in the main thread, otherwise there are issues with Wifi connections dropping
    while True:
        time.sleep(WEATHER_UPDATE)
        ntpsync.sync_time(LOCK)
        weather.update_weather(WEATHER_DATA, LOCK)

# start threads
_thread.start_new_thread(background_thread, ())
main_thread()