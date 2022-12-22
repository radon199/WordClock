import time
import ntptime
import network
import uasyncio
from machine import RTC

import connection

CONNECTION_TIMEOUT = 3

# Connect to the wifi network and sync the RTC to the UTC time returned from NTP
async def sync_time(frequency, loop=True):
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
            try:
                # Set the system time to UTC from NTP time
                ntptime.settime()
                print("RTC Time updated")
                next_sleep = frequency
            except:
                print("Unable to get time from NTP. Time not set.")
                # Sleep for only 5 seconds before trying again
                next_sleep = 5
        
        if loop:
            await uasyncio.sleep(next_sleep)
