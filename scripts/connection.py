import network
import time

from machine import Pin

from secrets import ssid, password
import utils
import neopixelarray
from colour import RED, GREEN, YELLOW

TIMEOUT = 10


def connect(max_retries):
    # Connect to wifi if not already connected
    status = network.STAT_IDLE
    for i in range(max_retries):
        print("Connection timeout : {}".format(str(i)))
        status = connect_once()
        if status == network.STAT_GOT_IP:
            break
    time.sleep(1)
    return status


def connect_once():
    wlan = network.WLAN(network.STA_IF)
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
    for i in range(TIMEOUT):
        status = wlan.status()
        if (status == network.STAT_CONNECT_FAIL or
            status == network.STAT_NO_AP_FOUND or
            status == network.STAT_WRONG_PASSWORD or
            status == network.STAT_GOT_IP):
            break
        print("Waiting for connection...")
        neopixelarray.blink_once(*neopixelarray.NETWORK_INDEX, YELLOW, 50)
        time.sleep(1)
    
    # Check after max timeout if the connection is good or not
    if wlan.status() != network.STAT_GOT_IP:
        print("Network connection failed")
        print(wlan.status())
        neopixelarray.blink(*neopixelarray.NETWORK_INDEX, RED, 3, 50, 200)
        return wlan.status()
    else:
        print("Connected to " + ssid)
        status = wlan.ifconfig()
        print("IP = " + status[0])
        neopixelarray.blink(*neopixelarray.NETWORK_INDEX, GREEN, 3, 50, 200)
        return network.STAT_GOT_IP
