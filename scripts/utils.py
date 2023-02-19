from machine import Pin
from time import sleep_ms
import network

import psttimezone
from datetime import datetime, timezone


# Lerp between colors
def color_lerp(A, B, alpha):
    return (min(int(A[0] * alpha) + int(B[0] * (1.0 - alpha)), 255),
            min(int(A[1] * alpha) + int(B[1] * (1.0 - alpha)), 255),
            min(int(A[2] * alpha) + int(B[2] * (1.0 - alpha)), 255))


# Return if the passed integer is even or odd
def is_odd(value):
    return bool(int(value) % 2)


# Convert an x, y array index to a linear index into the neopixel array
def array_index_to_linear_index(x, y, width, height):
    assert x > -1 and x < width and y > -1 and y < height

    # The linear index of the neopixel array starts in the lower left corner at 0,0 and travels left to right on even rows and right to left on odd rows
    # This is to make the wiring easier in the physical clock. Thus we should subtract the x value from 15 on every odd row
    if is_odd(y):
        x = (width-1) - x
    
    return (int(y) * height) + int(x)


# Slow debug print of the words in the word list based on the clock face
def debug_print_clock(words, width, height):
    print("- - - - - - - - - - - - - - - -")
    for y in range(0, height):
        # From top to bottom
        y = (height-1) - y
        # Store all characters in a line in a list
        characters = []
        for x in range(0, width):
            found = False
            for word in words:
                if word.y == y:
                    if x >= word.start_x and x <= word.end_x:
                        offset = x - word.start_x
                        characters.append(word.string[offset])
                        found = True
            if not found:
                characters.append("_")
            
        print(" ".join(characters))
    print("- - - - - - - - - - - - - - - -")


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