import uasyncio
from utils import is_quiet_hours, get_local_time
from datetime import datetime, timedelta

PRESENCE_DELAY = 60

# Async loop
async def update_presence_loop(data):
    while True:
        update_presence(data)
        print("Next presence update in {} seconds".format(PRESENCE_DELAY))
        await uasyncio.sleep(PRESENCE_DELAY)


def update_presence(data):
    # Early out if presene is already zero
    if not data.has_presence():
        print("Presence already zero. Skipping presence check.")
        return
    
    # Don't update presence outside quite hours
    if not is_quiet_hours(get_local_time()):
        print("Not quiet hours. Skipping presence check.")
        return

    # If there is presence then decrement it
    # The callback in the data object will handle resetting and turning on the display
    data.decrement_presence()