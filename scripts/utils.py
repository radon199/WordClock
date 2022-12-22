from machine import Pin
from time import sleep_ms
import network

import psttimezone
from datetime import datetime, timezone

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