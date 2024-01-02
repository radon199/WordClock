import neopixel
import machine
import time
import _thread
from utils import array_index_to_linear_index, is_low_light
from colour import Colour, BLACK

# Size Constants
WIDTH  = 16
HEIGHT = 16

# Pin Constants
OUTPUT = 22

# Fade Constants
STEPS  = 48
STEP   = 1.0 / float(STEPS)
PERIOD = 100
PERIOD_PER_STEP = int(PERIOD / STEPS)

# Intensity Mult
INTENSITY = 0.25
LOW_LIGHT_INTENSITY = 0.05

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
ARRAY.fill(BLACK.to_tuple())
ARRAY.write()

# If the neopixels are active
ACTIVE = True

# The active words on the ARRAY
CURRENT_WORDS = []
CURRENT_COLOUR = BLACK


# Set the array as active, and fade in any words, if not already active
def set_active():
    global ACTIVE
    if not ACTIVE:
        fade_in_array()
        ACTIVE = True


# Set the array as inactive, and fade out any current words, if not already inactive
def set_inactive():
    global ACTIVE
    if ACTIVE:
        fade_out_array()
        ACTIVE = False


# Get the value in the array
def get_value(x, y):
    value = ARRAY[array_index_to_linear_index(x, y, WIDTH, HEIGHT)]
    return Colour(value[0], value[1], value[2])


# Set the value in the array
def set_value(x, y, value):
    ARRAY[array_index_to_linear_index(x, y, WIDTH, HEIGHT)] = value.to_tuple()


# Clear the array, but keep the 
def clear_array(write=True, keep=True):
    if keep:
        N = get_value(*NETWORK_INDEX)
        C = get_value(*CLOCK_INDEX)
        W = get_value(*WEATHER_INDEX)
        P = get_value(*PRESENCE_INDEX)
    ARRAY.fill(BLACK.to_tuple())
    if keep:
        set_value(*NETWORK_INDEX, N)
        set_value(*CLOCK_INDEX, C)
        set_value(*WEATHER_INDEX, W)
        set_value(*PRESENCE_INDEX, P)
    if write:
        write_array()
    

# Send the data to the matrix
def write_array():
    ARRAY.write()


# Return a reference to the neopixel array
def get_array():
    return ARRAY


def get_array_lock():
    return ARRAY_LOCK


# Updates the words on the array, fading out the words that are no longer on the array, and then fading in any new ones.
def update_words(words, colour, linear_fade):
    # Declare CURRENT_WORDS as global, so we can assign it instead of clearing and extending it
    global CURRENT_WORDS
    global CURRENT_COLOUR
    
    # Compute the overall intensity for the light conditions and apply it to the input color
    colour *= LOW_LIGHT_INTENSITY if is_low_light() else INTENSITY

    # If the array is not active, then simply store the updated time
    if not ACTIVE:
        if ARRAY_LOCK.acquire(1, 5):
            CURRENT_WORDS = words
            CURRENT_COLOUR = colour
            ARRAY_LOCK.release()
        return
    
    if linear_fade:
        # Fade out all words
        fade_out_array()

        if ARRAY_LOCK.acquire(1, 5):
            # for each word fade them on one at a time
            for word in words:
                alpha = 0.0
                for i in range(STEPS+1):
                    # modulated colour value per step
                    alpha = min(1.0, alpha + STEP)
                    mix_colour = colour * alpha

                    # Write the modulated value to the array
                    word.fill_neopixel(ARRAY, mix_colour)
                    write_array()

                    time.sleep_ms(PERIOD_PER_STEP)
            
            # Update the current words with this set, so we can compare next iteration
            CURRENT_WORDS = words
            # Update the current colour with this colour, so we can compare next iteration
            CURRENT_COLOUR = colour

            ARRAY_LOCK.release()
    else:
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

        if ARRAY_LOCK.acquire(1, 5):
            # Fade out the words that need to be removed, if they exist
            if remove:
                alpha = 1.0
                for i in range(STEPS+1):
                    # modulated colour value per step
                    alpha = max(0.0, alpha - STEP)
                    mix_colour = CURRENT_COLOUR * alpha

                    # Write the modulated value to the array
                    for word in remove:
                        word.fill_neopixel(ARRAY, mix_colour)
                    write_array()

                    time.sleep_ms(PERIOD_PER_STEP)

            # Alter the colour of any existing words
            if keep:
                if colour != CURRENT_COLOUR:
                    alpha = 0.0
                    for i in range(STEPS+1):
                        # modulated colour value per step
                        alpha = min(1.0, alpha + STEP)
                        mix_colour = colour.lerp(CURRENT_COLOUR, alpha)

                        # Write the modulated value to the array
                        for word in keep:
                            word.fill_neopixel(ARRAY, mix_colour)
                        write_array()

                        time.sleep_ms(PERIOD_PER_STEP)

            # Fade in the words that need to be added
            if add:
                alpha = 0.0
                for i in range(STEPS+1):
                    # modulated colour value per step
                    alpha = min(1.0, alpha + STEP)
                    mix_colour = colour * alpha

                    # Write the modulated value to the array
                    for word in add:
                        word.fill_neopixel(ARRAY, mix_colour)
                    write_array()

                    time.sleep_ms(PERIOD_PER_STEP)
            
            # Update the current words with this set, so we can compare next iteration
            CURRENT_WORDS = words
            # Update the current colour with this colour, so we can compare next iteration
            CURRENT_COLOUR = colour

            ARRAY_LOCK.release()


# Fade in the words in the array
def fade_in_array():
    ARRAY_LOCK.acquire()
    alpha = 0.0
    for i in range(STEPS+1):
        # modulated colour value per step
        alpha = min(1.0, alpha + STEP)
        current_colour = CURRENT_COLOUR * alpha

        # Write the modulated value to the array
        for word in CURRENT_WORDS:
            word.fill_neopixel(ARRAY, current_colour)
        write_array()

        time.sleep_ms(PERIOD_PER_STEP)
    ARRAY_LOCK.release()


# Fade out the words in the array
def fade_out_array():
    ARRAY_LOCK.acquire()
    alpha = 1.0
    for i in range(STEPS+1):
        # modulated colour value per step
        current_colour = CURRENT_COLOUR * alpha
        alpha = max(0.0, alpha - STEP)

        # Write the modulated value to the array
        for word in CURRENT_WORDS:
            word.fill_neopixel(ARRAY, current_colour)
        write_array()

        time.sleep_ms(PERIOD_PER_STEP)

    # Clear the array to make sure it is fully off.
    clear_array(keep=False)
    ARRAY_LOCK.release()


# Turn on pixel
def turn_on(x, y, colour):
    set_value(x, y, colour)
    write_array()


# Turn off pixel
def turn_off(x, y):
    set_value(x, y, BLACK)
    write_array()


# Blink a pixel once
def blink_once(x, y, colour, duration_ms, restore=False):
    ARRAY_LOCK.acquire()
    
    old_value = get_value(x, y)

    set_value(x, y, colour)
    write_array()

    time.sleep_ms(duration_ms)

    set_value(x, y, old_value if restore else BLACK)
    write_array()

    ARRAY_LOCK.release()


# Blink a pixel in the array by the count and duration
def blink(x, y, colour, blink_count, duration_ms, delay_ms, restore=False):
    for i in range(0, blink_count):
        blink_once(x, y, colour, duration_ms)
        time.sleep_ms(delay_ms)


# Run at startup to check the array
def bootup_check():
    ARRAY_LOCK.acquire()
    x = 0
    for y in range(HEIGHT):
        for z in range(0, 3):
            set_value(x, y, Colour(255*int(z==0), 255*int(z==1), 255*int(z==2)))
            write_array()
            
            time.sleep(0.01)

            set_value(x, y, BLACK)
            write_array()
    clear_array(write=True, keep=False)
    ARRAY_LOCK.release()
