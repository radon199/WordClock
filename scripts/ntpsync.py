import ntptime
import network
import uasyncio
from machine import RTC
from utils import get_local_time
from datetime import datetime, timedelta

import connection
import neopixelarray
from colour import RED, GREEN, YELLOW
from utils import get_local_time

CONNECTION_TIMEOUT = 3
NTP_TIMEOUT = 3

# Async loop
async def sync_time_loop(data_lock):
    while True:
        sync_time(data_lock)
        current_time = get_local_time()
        # Time to 2am the next day
        next_fetch = current_time - (current_time.replace(hour=2, minute=0, second=0, microsecond=0) + timedelta(days=1))
        delay = abs(int(next_fetch.total_seconds()))
        print("Next time update in {} seconds".format(delay))
        await uasyncio.sleep(delay)


# Connect to the wifi network and sync the RTC to the UTC time returned from NTP
def sync_time(data):
    print("Updating NTP Time...")
    neopixelarray.turn_on(*neopixelarray.CLOCK_INDEX, YELLOW)
    # Connect to wifi if not already connected
    status = connection.connect(CONNECTION_TIMEOUT)

    if status == network.STAT_GOT_IP:
        for i in range(NTP_TIMEOUT):
            try:
                # Set the system time to UTC from NTP time, do so within the data lock, as the clock might be reading this time
                data.lock.acquire()
                ntptime.settime()
                data.lock.release()
                print("RTC Time updated")
                neopixelarray.blink_once(*neopixelarray.CLOCK_INDEX, GREEN, 50)
                return
            except:
                print("Unable to get time from NTP. Time not set.")
                neopixelarray.blink(*neopixelarray.CLOCK_INDEX, RED, 3, 50, 200)
    # Did not connect to network
    neopixelarray.blink(*neopixelarray.CLOCK_INDEX, RED, 3, 50, 200)