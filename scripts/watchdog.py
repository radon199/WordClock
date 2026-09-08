import uasyncio
from machine import reset
from datetime import timedelta
from utils import get_local_time

# Async loop
async def feed_watchdog_loop(data):
    while True:
        check_clock_watchdog(data)
        # Wait 5 minutes
        await uasyncio.sleep(300)


# Check if the clock thread is running
def check_clock_watchdog(data):
    current_time = get_local_time()
    if data.lock.acquire(1, 5):
        time_delta = current_time - data.last_clock_time
        data.lock.release()
        # Compare the current time to the last clock time, if it exceeds 3 minutes the clock has stopped
        # The clock thread updates its time every minute, so 3 minutes is a safe buffer
        if time_delta > timedelta(minutes=3):
            print("Clock watchdog reset")
            reset()
            return

    # Store the last time this function ran
    data.last_main_time = current_time

    print("Clock watchdog fed without issues")


# Check if the main thread is running
def check_main_watchdog(data):
    current_time = get_local_time()
    if data.lock.acquire(1, 5):
        time_delta = current_time - data.last_main_time
        data.lock.release()
        # Compare the current time to the last main time, if it exceeds 15 minutes the main thread has stopped
        # The main thread updates its time every 5 minutes, but may have long running processes
        if time_delta > timedelta(minutes=15):
            print("Main watchdog reset")
            reset()
            return

    print("Main watchdog fed without issues")
