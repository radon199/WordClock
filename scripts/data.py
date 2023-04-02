import _thread
import micropython
from machine import Pin
from datetime import datetime, timezone

# Allow for errors from the IRQ
micropython.alloc_emergency_exception_buf(100)

# Presence input, 1 means activity, 0 is not active
PRESENCE_PIN = Pin(20, Pin.IN)

# The maximum value to count to for presence
PRESENCE_MAX = 30

# Store persistant data
class Data:
    def __init__(self):
        # The temperature in degrees celsius
        self.temp = 0
        # The current weather condition in plain text
        self.condition = None
        # The Sunrise and Sunset time as a datetime object in utc
        self.sunrise = datetime.now(timezone.utc)
        self.sunset = datetime.now(timezone.utc)
        # Presence stack, starts at 30 and is decremeneted by the clock
        self.presence_count = 30
        # Lock for getting and setting the data
        self.lock = _thread.allocate_lock()
        # Create a reference to the increment presence function, it cannot be used directly in the IRQ
        self._reset_presence_ref = self.reset_presence
        # Add an interupt to the presence Pin
        PRESENCE_PIN.irq(handler=self.presence_callback, trigger=Pin.IRQ_RISING)


    # Callback for presence interupt
    def presence_callback(self, pin):
        # Schedual the increment of the presence count, this avoids any issues with functions that were interupted
        micropython.schedule(self._reset_presence_ref, None)


    # Actual function that resets the 
    def reset_presence(self, arg):
        self.lock.acquire()
        self.presence_count = PRESENCE_MAX
        self.lock.release()


    # Decrement the presence count
    def decrement_presence(self):
        self.lock.acquire()
        if self.presence_count > 0:
            self.presence_count -= 1
        self.lock.release()


    def __str__(self):
        return "(temp={}, condition={}, sunrise={}, sunset={})".format(self.temp, self.condition, self.sunrise, self.sunset)