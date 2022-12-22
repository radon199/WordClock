import uasyncio
from datetime import datetime, timezone

from utils import get_local_time
import weather

async def update_face(weather_data):
    # Run forever
    while True:
        time = get_local_time()
        
        # Hour modulo 12 gets us 12 form 24 hour
        hour = time.hour % 12
        minute = time.minute
    
        if minute > 30:
            to_past = "to"
            hour = hour + 1
            minute = 60 - minute
        else:
            to_past = "past"
        
        # The modulo above 
        if hour == 0:
            hour = str(12)
        else:
            hour = str(hour)
            
        minute = str(minute)
        
        if weather_data.temp <= 0:
            temp = "cold"
        elif weather_data.temp <= 12:
            temp = "cool"
        elif weather_data.temp <= 22:
            temp = "warm"
        else:
            temp = "hot"
            
        sunrise = weather_data.sunrise.astimezone(timezone.pst)
        sunset = weather_data.sunset.astimezone(timezone.pst)
            
        string = "The current time is {minute} minutes {to_past} {hour} and {temp}. Sunrise is at {sunrise} and sunset is at {sunset}".format(
            minute=minute,
            hour=hour,
            to_past=to_past,
            temp=temp,
            sunrise=sunrise,
            sunset=sunset)
        
        print(string)
        
        # Wait for the next minute to start. If this or other tasks delayed the running of this task, the below will compensate.
        # It is still possible to be delayed from the minute if a long running process is active on the minute itself.
        delay = 60 - int(get_local_time().second) # Time in seconds to end of minute
        await uasyncio.sleep(delay)