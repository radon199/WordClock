from machine import Pin
from time import sleep_ms
import network

import psttimezone
from datetime import datetime, timezone


# Return if the passed integer is even or odd
def is_odd(value):
    return bool(int(value) % 2)


# Convert an x, y array index to a linear index into the neopixel array
def array_index_to_linear_index(x, y):
    assert x > -1 and x < 16 and y > -1 and y < 16

    # The linear index of the neopixel array starts in the lower left corner at 0,0 and travels left to right on even rows and right to left on odd rows
    # This is to make the wiring easier in the physical clock. Thus we should subtract the x value from 15 on every odd row
    odd_row = is_odd(y)
    if odd_row:
        x = 15 - x
    
    return (int(y) * 16) + int(x)


def blink_once(duration_ms):
    led = Pin("LED", Pin.OUT)
    led.on()
    sleep_ms(duration_ms)
    led.off()


def blink(blink_count, duration_ms, delay_ms):
    led = Pin("LED", Pin.OUT)
    for i in range(0, blink_count):
        led.on()
        sleep_ms(duration_ms)
        led.off()
        sleep_ms(delay_ms)
        

def get_wlan():
    return network.WLAN(network.STA_IF)
        

def is_wlan_connected():
    return get_wlan().isconnected()


def get_utc_time():
    return datetime.now(timezone.utc)


def get_local_time():
    utc = get_utc_time()
    return utc.astimezone(timezone.pst)