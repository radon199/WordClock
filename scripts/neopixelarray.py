import neopixel
import machine
import time
from utils import array_index_to_linear_index

# Constants
WIDTH  = 16
HEIGHT = 16
OUTPUT = 22

# Indicator index
NETWORK_INDEX = (0, 0)
CLOCK_INDEX   = (1, 0)
WEATHER_INDEX = (2, 0)

# Output pin
OUTPUT_PIN = machine.Pin(OUTPUT)

# Global initalization
ARRAY = neopixel.NeoPixel(OUTPUT_PIN, WIDTH*HEIGHT)
ARRAY.fill((0,0,0))
ARRAY.write()

# Turn on pixel
def turn_on(x, y, color):
    set_value(x, y, color)
    ARRAY.write()


# Turn off pixel
def turn_off(x, y):
    set_value(x, y, (0,0,0))
    ARRAY.write()


# Blink a pixel once
def blink_once(x, y, color, duration_ms):
    set_value(x, y, color)
    ARRAY.write()
    time.sleep_ms(duration_ms)
    set_value(x, y, (0,0,0))
    ARRAY.write()


# Blink a pixel in the array by the count and duration
def blink(x, y, color, blink_count, duration_ms, delay_ms):
    for i in range(0, blink_count):
        blink_once(x, y, color, duration_ms)
        time.sleep_ms(delay_ms)


# Get the value in the array
def get_value(x, y):
    return ARRAY[array_index_to_linear_index(x, y, WIDTH, HEIGHT)]


# Set the value in the array
def set_value(x, y, value):
    ARRAY[array_index_to_linear_index(x, y, WIDTH, HEIGHT)] = value


# Clear the array, but keep the 
def clear_array(keep=True):
    if keep:
        N = get_value(*NETWORK_INDEX)
        C = get_value(*CLOCK_INDEX)
        W = get_value(*WEATHER_INDEX)
    ARRAY.fill((0,0,0))
    if keep:
        set_value(*NETWORK_INDEX, N)
        set_value(*CLOCK_INDEX, C)
        set_value(*WEATHER_INDEX, W)
    ARRAY.write()
    

# Send the data to the matrix
def write_array():
    ARRAY.write()


# Return a reference to the neopixel array
def get_array():
    return ARRAY


# Run at startup to check the array
def bootup_check():
    x = 0
    for y in range(0, HEIGHT):
        for z in range(0, 3):
            set_value(x, y, (255*int(z==0), 255*int(z==1), 255*int(z==2)))
            ARRAY.write()
            
            time.sleep(0.05)
            set_value(x, y, (0,0,0))
            ARRAY.write()
    clear_array()
