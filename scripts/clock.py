import uasyncio
from datetime import datetime, timezone

from utils import get_local_time, array_index_to_linear_index, debug_print_clock
import weather


# Stores the linear index to a word, and can add themselves to a neopixel array
class Word:
    def __init__(self, string, x, length, y):
        self.string = string
        self.start_x = x
        self.end_x = x + (length - 1)
        self.y = y
        
    def __str___(self):
        return self.string

    def fill_neopixel(self, array, color):
        start_index = array_index_to_linear_index(self.start_x, self.y)
        end_index = array_index_to_linear_index(self.end_x, self.y)

        # Early exit for single character words
        if start_index == end_index:
            array[start_index] = color
            return

        # If start is after end, switch them so that range is always forward
        if start_index > end_index:
            start_index, end_index = end_index, start_index
        
        # Iterate over the range and fill the neopixel array
        for i in range(start_index, end_index):
            array[i] = color


# Word Constants
THE       = Word("THE", 0, 3, 15)
TIME      = Word("TIME", 4, 4 , 15)
IS        = Word("IS", 9, 2, 15)
MINUTES   = Word("MINUTES", 0, 7, 8)
PAST      = Word("PAST", 8, 4, 8)
TO        = Word("TO", 11, 2, 8)
OCLOCK    = Word("OCLOCK", 0, 6, 4)
IN        = Word("IN", 7, 2, 4)
AT        = Word("AT", 9, 2, 4)
NIGHT     = Word("NIGHT", 0, 5, 3)
THE_2     = Word("THE", 4, 3, 3)
MORNING   = Word("MORNING", 8, 7, 3)
EVENING   = Word("EVENING", 0, 7, 2)
AFTERNOON = Word("AFTERNOON", 7, 9, 2)
AND       = Word("AND", 0, 3, 1)
COLD      = Word("COLD", 4, 4, 1)
COOL      = Word("COOL", 8, 4, 1)
COOLING   = Word("COOLING", 8, 7, 1)
WARM      = Word("WARM", 5, 4, 0)
WARMING   = Word("WARMING", 5, 7, 0)
HOT       = Word("HOT", 12, 3, 0)


MINUTES_DICT = {
    30 : Word("HALF", 12, 4, 15),
    20 : Word("TWENTY", 7, 6, 14),
    19 : Word("NINETEEN", 8, 9, 11),
    18 : Word("EIGHTEEN", 0, 8, 12),
    17 : Word("SEVENTEEN", 0, 9, 11),
    16 : Word("SIXTEEN", 3, 7, 13),
    15 : Word("QUARTER", 0, 7, 14),
    14 : Word("FOURTEEN", 0, 8, 10),
    13 : Word("THIRTEEN", 8, 8, 10),
    12 : Word("TWELVE", 0, 6, 9),
    11 : Word("ELEVEN", 5, 6, 9),
    10 : Word("TEN", 0, 3, 13),
    9  : Word("NINE", 8, 4, 11),
    8  : Word("EIGHT", 0, 5, 12),
    7  : Word("SEVEN", 0, 5, 11),
    6  : Word("SIX", 3, 3, 13),
    5  : Word("Five", 8, 4, 12),
    4  : Word("FOUR", 0, 4, 10),
    3  : Word("THREE", 11, 5, 9),
    2  : Word("TWO", 10, 3, 13),
    1  : Word("ONE", 12, 3, 13),
}


HOURS_DICT = {
    11 : Word("ELEVEN", 4, 6, 7),
    10 : Word("TEN", 12, 3, 5),
    9  : Word("NINE", 9, 4, 7),
    8  : Word("EIGHT", 8, 5, 5),
    7  : Word("SEVEN", 0, 5, 6),
    6  : Word("SIX", 13, 3, 7),
    5  : Word("FIVE", 5, 4, 5),
    4  : Word("FOUR", 0, 4, 5),
    3  : Word("THREE", 5, 5, 6),
    2  : Word("TWO", 0, 3, 7),
    1  : Word("ONE", 2, 3, 7),
    0  : Word("TWELVE", 10, 6, 6),
}
        

async def update_face(weather_data):
    # Run forever
    while True:
        time = get_local_time()
        
        words = []
        # Add the words that are always lit
        words.extend([THE, TIME, IS])
        
        # Hour modulo 12 gets us 12 hours from 24 hour
        hour = time.hour % 12
        minute = time.minute
    
        # If it is passed 30 minutes we count up to the next hour due to space limitations of the clock
        if minute > 30:
            words.append(TO)
            # Hour 11 loops around to 0 if offset
            hour = 0 if hour > 11 else hour +1
            minute = 60 - minute
        else:
            words.append(PAST)
        
        # Append the hour word to the list
        assert hour >= 0 and hour <= 11
        words.append(HOURS_DICT.get(hour))

        # Append the minute word(s) to the list
        assert minute <= 30
        if minute > 0:
            # Simple case for minutes below 20 or exactly 30
            if minute <= 20 or minute == 30:
                words.append(MINUTES_DICT.get(minute))
            # For time between 20 and 30 we need to subtract 20 to get the single digit
            else:
                single = minute - 20
                if single > 0 and single < 9:
                    words.append(MINUTES_DICT.get(single))
            
            # Only append minutes if minute is above 0, and not quarter or or half
            if minute != 15 or minute != 30:
                words.append(MINUTES)
                
        # Append the time of day from the raw 24 hour time
        if time.hour < 5:
            words.extend([AT, NIGHT])
        elif time.hour < 12:
            words.extend([IN, THE_2, MORNING])
        elif time.hour < 18:
            words.extend([IN, THE_2, AFTERNOON])
        else:
            words.extend([IN, THE_2, EVENING])
        
        # Append the temperature
        words.append(AND)
        if weather_data.temp <= 0:
            words.append(COLD)
        elif weather_data.temp <= 12:
            words.append(COOL)
        elif weather_data.temp <= 22:
            words.append(WARM)
        else:
            words.append(HOT)
            
        sunrise = weather_data.sunrise.astimezone(timezone.pst)
        sunset = weather_data.sunset.astimezone(timezone.pst)
        
        debug_print_clock(words, 16, 16)
        
        # Wait for the next minute to start. If this or other tasks delayed the running of this task, the below will compensate.
        # It is still possible to be delayed from the minute if a long running process is active on the minute itself.
        delay = 60 - int(get_local_time().second) # Time in seconds to end of minute
        await uasyncio.sleep(delay)