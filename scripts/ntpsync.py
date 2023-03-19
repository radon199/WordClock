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
        retries = NTP_TIMEOUT
        while retries > 0:
            try:
                # Set the system time to UTC from NTP time, do so within the data lock, as the clock might be reading this time
                data_lock.acquire()
                ntptime.settime()
                data_lock.release()
                print("RTC Time updated")
                neopixelarray.blink_once(*neopixelarray.CLOCK_INDEX, neopixelarray.Green, 100)
                return
            except:
                print("Unable to get time from NTP. Time not set.")
                retries -= 1
                neopixelarray.blink(*neopixelarray.CLOCK_INDEX, neopixelarray.RED, 3, 50, 300)
                return
    # Did not connect to network
    neopixelarray.blink(*neopixelarray.CLOCK_INDEX, neopixelarray.RED, 3, 50, 300)