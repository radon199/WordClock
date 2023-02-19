import network
import time
import uasyncio

from machine import Pin

from secrets import ssid, password
import utils

TIMEOUT = 10


async def connect():
    wlan = utils.get_wlan()
    # If the wlan is already connected and to the correct ssid, then simply exit
    if wlan.isconnected() and wlan.config('ssid') == ssid:
        print("Already connected to " + ssid)
        status = wlan.ifconfig()
        print("IP = " + status[0])
        return network.STAT_GOT_IP

    # Set the wlan as active and connect using the stored ssid and password
    wlan.active(True)
    wlan.connect(ssid=ssid, key=password)

    # Wait for connection to be made or fail
    max_wait = TIMEOUT
    while max_wait > 0:
        status = wlan.status()
        if (status == network.STAT_CONNECT_FAIL or
            status == network.STAT_NO_AP_FOUND or
            status == network.STAT_WRONG_PASSWORD or
            status == network.STAT_GOT_IP):
            break
        max_wait -= 1
        print("Waiting for connection...")
        utils.blink_once(100)
        await uasyncio.sleep(1)
    
    # Check after max timeout if the connection is good or not
    if wlan.status() != network.STAT_GOT_IP:
        print("Network connection failed")
        print(wlan.status())
        return wlan.status()
    else:
        print("Connected to " + ssid)
        status = wlan.ifconfig()
        print("IP = " + status[0])
        utils.blink(5, 50, 300)
        return network.STAT_GOT_IP
