from datetime import datetime, timezone
import time

import neopixelarray
import utils
from data import Data
from colour import Colour, BLACK

# sort key function for words, in top to bottom and left to right order
def word_sort_key(word):
    # subtract y from pixel array height for reverse search
    return ((neopixelarray.HEIGHT - word.y) * neopixelarray.WIDTH) + word.start_x

# Stores the x,y position and length of a word, and can add themselves to a neopixel array via the fill_neopixel function
class Word:
    def __init__(self, string, x, y, colour=BLACK):
        # The text based representation of the word
        self.string = string
        # The starting x coodinate of the word
        self.start_x = x
        # The ending x coordinate of the word, from the string length
        self.end_x = x + (len(self.string)-1)
        # The overall y coordinate of the word
        self.y = y
        # The color of the word
        self.colour = colour
        
    def __str___(self):
        return self.string

    def fill_neopixel(self, array, colour):
        # Make sure the range goes past the end of the word, as range stops before the ending index
        for x in range(self.start_x, self.end_x+1):
            # Set each x value in the array to the colour
            neopixelarray.set_value(x, self.y, colour)


# Word Constants
THE       = Word("THE", 0, 15)
TIME      = Word("TIME", 4, 15)
IS        = Word("IS", 9, 15)
MINUTE    = Word("MINUTE", 0, 8)
MINUTES   = Word("MINUTES", 0, 8)
PAST      = Word("PAST", 8, 8)
TO        = Word("TO", 11, 8)
OCLOCK    = Word("OCLOCK", 0, 4)
IN        = Word("IN", 7, 4)
AT        = Word("AT", 9, 4)
NIGHT     = Word("NIGHT", 0, 3)
THE_2     = Word("THE", 4, 3)
MORNING   = Word("MORNING", 8, 3)
EVENING   = Word("EVENING", 0, 2)
AFTERNOON = Word("AFTERNOON", 7, 2)
AND       = Word("AND", 0, 1)
COLD      = Word("COLD", 4, 1)
COOL      = Word("COOL", 8, 1)
COOLING   = Word("COOLING", 8, 1)
WARM      = Word("WARM", 5, 0)
WARMING   = Word("WARMING", 5, 0)
HOT       = Word("HOT", 12, 0)


# Minute Word Constants
MINUTES_DICT = {
    30 : Word("HALF", 12, 15),
    20 : Word("TWENTY", 7, 14),
    19 : Word("NINETEEN", 8, 11),
    18 : Word("EIGHTEEN", 0, 12),
    17 : Word("SEVENTEEN", 0, 11),
    16 : Word("SIXTEEN", 3, 13),
    15 : Word("QUARTER", 0, 14),
    14 : Word("FOURTEEN", 0, 10),
    13 : Word("THIRTEEN", 8, 10),
    12 : Word("TWELVE", 0, 9),
    11 : Word("ELEVEN", 5, 9),
    10 : Word("TEN", 0, 13),
    9  : Word("NINE", 8, 11),
    8  : Word("EIGHT", 0, 12),
    7  : Word("SEVEN", 0, 11),
    6  : Word("SIX", 3, 13),
    5  : Word("Five", 8, 12),
    4  : Word("FOUR", 0, 10),
    3  : Word("THREE", 11, 9),
    2  : Word("TWO", 10, 13),
    1  : Word("ONE", 12, 13),
}


# Hour word constants
HOURS_DICT = {
    11 : Word("ELEVEN", 4, 7),
    10 : Word("TEN", 12, 5),
    9  : Word("NINE", 9, 7),
    8  : Word("EIGHT", 8, 5),
    7  : Word("SEVEN", 0, 6),
    6  : Word("SIX", 13, 7),
    5  : Word("FIVE", 5, 5),
    4  : Word("FOUR", 0, 5),
    3  : Word("THREE", 5, 6),
    2  : Word("TWO", 0, 7),
    1  : Word("ONE", 2, 7),
    0  : Word("TWELVE", 10, 6),
}


# Colours
COLOUR_DAY = Colour(255, 255, 255)
COLOUR_SUNRISE_SUNSET = Colour(255, 60, 0)
COLOUR_NIGHT = Colour(50, 50, 255)


def update_face(current_time, data):
    print("Update clock time")        

    # Holds the words to be active
    words = []
    # Add the words that are always lit
    words.extend([THE, TIME, IS])
    
    # Hour modulo 12 gets us 12 hours from 24 hour
    hour = current_time.hour % 12
    minute = current_time.minute

    # If it is passed 30 minutes we count up to the next hour due to space limitations of the clock
    if minute > 0:
        if minute > 30:
            words.append(TO)
            # Hour 11 loops around to 0 if offset
            hour = 0 if hour >= 11 else hour + 1
            minute = 60 - minute
        else:
            words.append(PAST)
    
    # Append the hour word to the list
    assert hour >= 0 and hour <= 11
    words.append(HOURS_DICT.get(hour))

    # Append the minute word(s) to the list
    assert minute <= 30
    # If minutes is 0, add OCLOCK to the words
    if minute == 0:
        words.append(OCLOCK)
    else:
        # Simple case for minutes below 20 or exactly 30
        if minute <= 20 or minute == 30:
            words.append(MINUTES_DICT.get(minute))
        # For time between 20 and 29 we need to subtract 20 to get the single digit
        else:
            # Add Twenty to the list
            words.append(MINUTES_DICT.get(20))
            single = minute - 20
            if single > 0 and single <= 9:
                words.append(MINUTES_DICT.get(single))
        
        # Append Minute is at 1 minute past or to the hour
        # Append Minutes if not quarter or half past
        if minute == 1:
            words.append(MINUTE)
        elif minute != 15 and minute != 30:
            words.append(MINUTES)
    
            
    # Append the time of day from the raw 24 hour time
    if current_time.hour < 5:
        words.extend([AT, NIGHT])
    elif current_time.hour < 12:
        words.extend([IN, THE_2, MORNING])
    elif current_time.hour < 18:
        words.extend([IN, THE_2, AFTERNOON])
    else:
        words.extend([IN, THE_2, EVENING])
    
    # Append the temperature
    words.append(AND)
    if data.temp <= 4:
        words.append(COLD)
    elif data.temp <= 12:
        words.append(COOL)
    elif data.temp <= 22:
        words.append(WARM)
    else:
        words.append(HOT)
    
    # Get sunrise and sunset times in local time, background thread might be updating the weather, so aquire the lock
    data.lock.acquire()
    sunrise = data.sunrise.astimezone(timezone.pst)
    sunset  = data.sunset.astimezone(timezone.pst)
    data.lock.release()
    # Copy the date from the current_time, so that we can compare them even if sunrise and sunset are the next or previous day
    sunrise = sunrise.replace(day = current_time.day)
    sunset = sunset.replace(day = current_time.day)
    
    # Choose night or daytime colour based on time before or after sunset, this will be modulated by the minutes to or from sunrise/sunset
    colour = COLOUR_DAY if ((sunrise < current_time) and (current_time < sunset)) else COLOUR_NIGHT

    # If within 1 hour of sunrise or sunset, lerp between the current colour and the sunrise/sunset colour
    minutes_to_sunrise = utils.get_time_difference_in_seconds(current_time, sunrise) / 60
    if minutes_to_sunrise < 60:
        # Alpha is a 0.0-1.0 value where 0.0 is sunrise and 1.0 is one hour either side
        alpha = minutes_to_sunrise / 60
        colour = colour.lerp(COLOUR_SUNRISE_SUNSET, alpha)

    minutes_to_sunset  = utils.get_time_difference_in_seconds(current_time, sunset) / 60
    if minutes_to_sunset < 60:
        # Alpha is a 0.0-1.0 value where 0.0 is sunset and 1.0 is one hour either side
        alpha = minutes_to_sunset / 60
        colour = colour.lerp(COLOUR_SUNRISE_SUNSET, alpha)

    # sort the words in their order on the clock face
    words.sort(key=word_sort_key)

    # Do the linear fade on the hour
    linear_fade = True if minute == 0 else False

    # Send the words to the array
    neopixelarray.update_words(words, colour, linear_fade)


# Update the words on the clock face
def start_clock_loop(data):
    # Run forever
    while True:
        # The background thread might be updating the time, block until it does
        data.lock.acquire()
        current_time = utils.get_local_time()
        data.lock.release()

        update_face(current_time, data)

        # Wait for the next minute to start. If this or other tasks delayed the running of this task, the below will compensate.
        # It is still possible to be delayed from the minute if a long running process is active on the minute itself.
        delay = 60 - int(utils.get_local_time().second) # Time in seconds to end of minute
        time.sleep(delay)