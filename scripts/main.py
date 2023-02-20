import _thread
import time

import neopixelarray
import clock
import ntpsync
import weather

WEATHER_UPDATE = 1800

# Global variable, hold the weather data
weather_data = weather.WeatherData()

# Weather and time lock
lock = _thread.allocate_lock()

print("Initalization...")
neopixelarray.bootup_check()
ntpsync.sync_time(lock)
weather.update_weather(weather_data, lock)
print("Initalization complete")

def background_thread():
    # update_face will run forever
    clock.update_face(weather_data, lock)

def main_thread():
    # Run forever. Sync time and update weather need to run in the main thread, otherwise there are issues with Wifi connections dropping
    while True:
        time.sleep(WEATHER_UPDATE)
        ntpsync.sync_time(lock)
        weather.update_weather(weather_data, lock)

# start threads
_thread.start_new_thread(background_thread, ())
main_thread()