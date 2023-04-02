import neopixel
import machine
import time
import _thread
from utils import array_index_to_linear_index, color_intensity, color_lerp

# Size Constants
WIDTH  = 16
HEIGHT = 16

# Pin Constants
OUTPUT = 22

# Fade Constants
STEPS  = 48
STEP   = 1.0 / float(STEPS)
PERIOD = 500
PERIOD_PER_STEP = int(PERIOD / STEPS)

# Color constants
BLACK  = (0,0,0)
WHITE  = (255,255,255)
RED    = (255,0,0)
YELLOW = (255,255,0)
GREEN  = (0,255,0)

# Indicator index
NETWORK_INDEX  = (0, 0)
CLOCK_INDEX    = (1, 0)
WEATHER_INDEX  = (2, 0)
PRESENCE_INDEX = (3, 0)

# Output pin
OUTPUT_PIN = machine.Pin(OUTPUT)

# Array lock
ARRAY_LOCK = _thread.allocate_lock()

# Global initalization
# This acts as a singleton so any part of the clock can write to the array
# This allows the background tasks to set the status indicators
ARRAY = neopixel.NeoPixel(OUTPUT_PIN, WIDTH*HEIGHT)
# Clear and write the array to black
ARRAY.fill(BLACK)
ARRAY.write()

# The active words on the ARRAY
CURRENT_WORDS = []
CURRENT_COLOR = BLACK

# Turn on pixel
def turn_on(x, y, color):
    set_value(x, y, color)
    ARRAY.write()


# Turn off pixel
def turn_off(x, y):
    set_value(x, y, BLACK)
    ARRAY.write()


# Blink a pixel once
def blink_once(x, y, color, duration_ms, lock=True):
    #if lock:
    #    ARRAY_LOCK.acquire()

    set_value(x, y, color)
    ARRAY.write()

    time.sleep_ms(duration_ms)

    set_value(x, y, BLACK)
    ARRAY.write()

    #if lock:
    #    ARRAY_LOCK.release()


# Blink a pixel in the array by the count and duration
def blink(x, y, color, blink_count, duration_ms, delay_ms):
    #ARRAY_LOCK.acquire()

    for i in range(0, blink_count):
        blink_once(x, y, color, duration_ms, lock=False)
        time.sleep_ms(delay_ms)

    #ARRAY_LOCK.release()


# Get the value in the array
def get_value(x, y):
    return ARRAY[array_index_to_linear_index(x, y, WIDTH, HEIGHT)]


# Set the value in the array
def set_value(x, y, value):
    ARRAY[array_index_to_linear_index(x, y, WIDTH, HEIGHT)] = value


# Clear the array, but keep the 
def clear_array(write=True, keep=True):
    #ARRAY_LOCK.acquire()
    if keep:
        N = get_value(*NETWORK_INDEX)
        C = get_value(*CLOCK_INDEX)
        W = get_value(*WEATHER_INDEX)
    ARRAY.fill(BLACK)
    if keep:
        set_value(*NETWORK_INDEX, N)
        set_value(*CLOCK_INDEX, C)
        set_value(*WEATHER_INDEX, W)
    if write:
        ARRAY.write()
    #ARRAY_LOCK.release()
    

# Send the data to the matrix
def write_array():
    ARRAY.write()


# Return a reference to the neopixel array
def get_array():
    return ARRAY


# Updates the words on the array, fading out the words that are no longer on the array, and then fading in any new ones.
def update_words(words, color):
    # Declare CURRENT_WORDS as global, so we can assign it instead of clearing and extending it
    global CURRENT_WORDS
    global CURRENT_COLOR

    # In the current list of words, find out what ones exist in the new set of words, and what ones need to be removed
    keep = []
    remove = []
    for existing in CURRENT_WORDS:
        if existing in words:
            keep.append(existing)
        else:
            remove.append(existing)
    
    # Filter the list of new words and remove any that already exist on the current array
    add = []
    for new in words:
        if new in keep:
            continue
        else:
            add.append(new)

    ARRAY_LOCK.acquire()
    # Fade out the words that need to be removed, if they exist
    if remove:
        alpha = 1.0
        for i in range(STEPS+1):
            # modulated color value per step
            current_color = color_intensity(CURRENT_COLOR, alpha)
            alpha = max(0.0, alpha - STEP)

            # Write the modulated value to the array
            for word in remove:
                word.fill_neopixel(ARRAY, current_color)
            ARRAY.write()

            time.sleep_ms(PERIOD_PER_STEP)

    # Alter the color of any existing words
    if keep:
        if color != CURRENT_COLOR:
            alpha = 0.0
            for i in range(STEPS+1):
                # modulated color value per step
                alpha = min(1.0, alpha + STEP)
                mix_color = color_lerp(color, CURRENT_COLOR, alpha)
                for word in keep:
                    word.fill_neopixel(ARRAY, mix_color)
                ARRAY.write()

                time.sleep_ms(PERIOD_PER_STEP)

    # Fade in the words that need to be added
    if add:
        alpha = 0.0
        for i in range(STEPS+1):
            # modulated color value per step
            alpha = min(1.0, alpha + STEP)
            current_color = color_intensity(color, alpha)

            # Write the modulated value to the array
            for word in add:
                word.fill_neopixel(ARRAY, current_color)
            ARRAY.write()

            time.sleep_ms(PERIOD_PER_STEP)
    
    # Update the current words with this set, so we can compare next iteration
    CURRENT_WORDS = words
    # Update the current color with this color, so we can compare next iteration
    CURRENT_COLOR = color

    ARRAY_LOCK.release()


# Fade out the array
def fade_out_array():
    alpha = 1.0
    for i in range(STEPS+1):
        # modulated color value per step
        current_color = color_intensity(CURRENT_COLOR, alpha)
        alpha = max(0.0, alpha - STEP)

        # Write the modulated value to the array
        for word in remove:
            word.fill_neopixel(ARRAY, current_color)
        ARRAY.write()

        time.sleep_ms(PERIOD_PER_STEP)


# Run at startup to check the array
def bootup_check():
    #ARRAY_LOCK.acquire()
    x = 0
    for y in range(HEIGHT):
        for z in range(0, 3):
            set_value(x, y, (255*int(z==0), 255*int(z==1), 255*int(z==2)))
            ARRAY.write()
            
            time.sleep(0.01)

            set_value(x, y, (0,0,0))
            ARRAY.write()
    clear_array(write=True, keep=False)
    #ARRAY_LOCK.release()
