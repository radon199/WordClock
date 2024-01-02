import ntptime
import network
import uasyncio
import time
from machine import RTC
from utils import get_local_time
from datetime import datetime, timedelta

import connection
import neopixelarray
from colour import RED, GREEN, YELLOW
from utils import get_local_time

CONNECTION_TIMEOUT = 3
NTP_TIMEOUT = 3
NTP_WAIT = 2

# Async loop
async def sync_time_loop(data):
    while True:
        sync_time(data)
        current_time = get_local_time()
        # Time to 2am the next day
        next_fetch = (current_time.replace(hour=2, minute=30, second=0, microsecond=0) + timedelta(days=1)) - current_time
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
            print("Trying to update RTC time...")
            # Set the system time to UTC from NTP time, do so within the data lock, as the clock might be reading this time
            if data.lock.acquire(1, 5):
                got_time = False
                try:
                    ntptime.settime()
                    got_time = True
                    print("RTC Time updated")
                    neopixelarray.blink_once(*neopixelarray.CLOCK_INDEX, GREEN, 50)
                except:
                    print("Unable to get time from NTP. Time not set.")
                    neopixelarray.blink_once(*neopixelarray.CLOCK_INDEX, RED, 50)
                data.lock.release()
                if got_time:
                    return
            time.sleep(NTP_WAIT)
    # Did not connect to network
    neopixelarray.blink(*neopixelarray.CLOCK_INDEX, RED, 3, 50, 200)