import time
import ntptime
import network
from machine import RTC

import connection
import neopixelarray
from utils import get_local_time

CONNECTION_TIMEOUT = 3
NTP_TIMEOUT = 3

# Connect to the wifi network and sync the RTC to the UTC time returned from NTP
def sync_time(data_lock):
    print("Updating NTP Time...")
    neopixelarray.turn_on(*neopixelarray.CLOCK_INDEX, neopixelarray.YELLOW)
    # Connect to wifi if not already connected
    status = connection.connect(CONNECTION_TIMEOUT)

    if status == network.STAT_GOT_IP:
        for i in range(NTP_TIMEOUT):
            try:
                # Set the system time to UTC from NTP time, do so within the data lock, as the clock might be reading this time
                data_lock.acquire()
                ntptime.settime()
                data_lock.release()
                print("RTC Time updated")
                neopixelarray.blink_once(*neopixelarray.CLOCK_INDEX, neopixelarray.GREEN, 50)
                return
            except:
                print("Unable to get time from NTP. Time not set.")
                neopixelarray.blink(*neopixelarray.CLOCK_INDEX, neopixelarray.RED, 3, 50, 200)
    # Did not connect to network
    neopixelarray.blink(*neopixelarray.CLOCK_INDEX, neopixelarray.RED, 3, 50, 200)