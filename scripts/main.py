import _thread
import uasyncio
import time

import neopixelarray
from clock import start_clock_loop
from ntpsync import sync_time, sync_time_loop
from weather import update_weather, update_weather_loop
from data import Data


# Global variable that holds all state data
DATA = Data()


print("Initalization...")
neopixelarray.bootup_check()
sync_time(DATA)
update_weather(DATA)
print("Initalization complete")


# Background thread runs the clock face only on it's own, and loops every minute
def background_thread():
    # update_face will run forever
    start_clock_loop(DATA)


# Main thread runs the asyncio tasks for updating time and weather
async def main_thread():
    # Delay the start of this thread to prevent hitting the time and weather server
    time.sleep(30)
    # Create the async tasks
    sync_task = uasyncio.create_task(sync_time_loop(DATA))
    weather_task = uasyncio.create_task(update_weather_loop(DATA))
    await sync_task
    await weather_task


# Increase stack size for background thread, otherwise we hit the function limit
_thread.stack_size(16 * 1024)

# Start backgroud thread
_thread.start_new_thread(background_thread, ())

# Start main thread
try:
    uasyncio.run(main_thread())
finally:
    uasyncio.new_event_loop()