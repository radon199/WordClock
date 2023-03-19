import network
import time

from machine import Pin

from secrets import ssid, password
import utils
import neopixelarray

TIMEOUT = 10


def connect():
    wlan = utils.get_wlan()
    # If the wlan is already connected and to the correct ssid, then simply exit
    if wlan.isconnected() and wlan.config("ssid") == ssid:
            print("Already connected to {}. IP = {}".format(ssid, wlan.ifconfig()[0]))
            return network.STAT_GOT_IP

    # Set the wlan as active and connect using the stored ssid and password
    print("Starting new WiFi connection...")
    wlan.active(True)
    try:
        wlan.connect(ssid=ssid, key=password)
    except Exception as e:
        print("Connection failed.")
        print(e)
        return
    # Delay the start of the connection check
    time.sleep(1)

    # Wait for connection to be made or fail
    print("Starting timeout...")
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
        neopixelarray.blink_once(*neopixelarray.NETWORK_INDEX, neopixelarray.YELLOW, 100)
        time.sleep(1)
    
    # Check after max timeout if the connection is good or not
    if wlan.status() != network.STAT_GOT_IP:
        print("Network connection failed")
        print(wlan.status())
        neopixelarray.blink(*neopixelarray.NETWORK_INDEX, neopixelarray.RED, 3, 50, 300)
        return wlan.status()
    else:
        print("Connected to " + ssid)
        status = wlan.ifconfig()
        print("IP = " + status[0])
        neopixelarray.blink(*neopixelarray.NETWORK_INDEX, neopixelarray.GREEN, 3, 50, 300)
        return network.STAT_GOT_IP
