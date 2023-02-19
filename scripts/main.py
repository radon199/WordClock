import uasyncio
import time

import clock
import ntpsync
import weather


# Scheduler body, all tasks run forever, and so this will never exit
async def main():
    # Setup weather data
    weather_data = weather.WeatherData()

    # Task that syncs the time from NTP
    sync_task = uasyncio.create_task(ntpsync.sync_time(3600))
    
    # Task that syncs the weather data from openweather
    weather_task = uasyncio.create_task(weather.get_temperature(weather_data, 1800))
    
    # Task that updates the clock face
    face_task = uasyncio.create_task(clock.update_face(weather_data))
    await face_task
    
try:
    print("Start main loop")
    uasyncio.run(main())
finally:
    uasyncio.new_event_loop()