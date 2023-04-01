import _thread
import time

import neopixelarray
from clock import start_clock_loop
from ntpsync import sync_time
from weather import WeatherData, update_weather

# Update weather and time once an hour
UPDATE_TIME = 3600

# Global variable, hold the weather data
WEATHER_DATA = WeatherData()

# Weather and time lock
LOCK = _thread.allocate_lock()

print("Initalization...")
neopixelarray.bootup_check()
sync_time(LOCK)
update_weather(WEATHER_DATA, LOCK)
print("Initalization complete")

def background_thread():
    # update_face will run forever
    start_clock_loop(WEATHER_DATA, LOCK)

def main_thread():
    # Run forever. Sync time and update weather need to run in the main thread, otherwise there are issues with Wifi connections dropping
    while True:
        time.sleep(UPDATE_TIME)
        sync_time(LOCK)
        update_weather(WEATHER_DATA, LOCK)

# Increase stack size for background thread, otherwise we hit the function limit
_thread.stack_size(16 * 1024)

# start threads
_thread.start_new_thread(background_thread, ())
main_thread()