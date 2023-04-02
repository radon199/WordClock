from machine import Pin, ADC
from time import sleep_ms
import network
import neopixel
import psttimezone
from datetime import datetime, timezone


# The number of samples to take from the light sensor
LIGHT_SAMPLES = 3


# Global ADC for the light photoresistor
LIGHT_ADC = ADC(Pin(28))


# Clamp a value between 255 and 0
def byte_clamp(value):
    return max(min(int(value), 255), 0)


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
    for i in range(blink_count):
        led.on()
        sleep_ms(duration_ms)
        led.off()
        sleep_ms(delay_ms)


# Get the current time in UTC from datetime
def get_utc_time():
    return datetime.now(timezone.utc)


# Get the current time in UTC, and convert it to PST
def get_local_time():
    return get_utc_time().astimezone(timezone.pst)


# Get the difference between two datetimes in seconds, regardless of order
def get_time_difference_in_seconds(t1, t2):
    if t1 == t2:
        return 0

    if t2 > t1:
        delta = t1 - t2
    else:
        delta = t2 - t1
    
    return abs(delta.total_seconds())


# Get the light intensity as a raw 16bit int
def get_light_intensity():
    return LIGHT_ADC.read_u16()


# Check if the current light value is considered low light
def is_low_light():
    # Average over a specified number of samples
    value = 0
    for i in range(LIGHT_SAMPLES):
        value += get_light_intensity()
    value /= LIGHT_SAMPLES
    return value < 8000