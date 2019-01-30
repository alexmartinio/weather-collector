import statistics
import time
from datetime import datetime

import Sensors
from WeatherDatabase import *

# Time interval to report (seconds)
interval = 5
store_speeds = []

# Rain interval # 3600 = 1 hour
rain_interval = 3600

# facing 305 is 90
# 360 - 305 = 55 + 90 = 145 North
NORTH = 145

_rainfall = Sensors.Rain()
speed = Sensors.WindSpeed()
_ambient_temperature = Sensors.AmbientTemperature()
_pressure = Sensors.Pressure()
_humidity = Sensors.Humidity()

# This takes 5 minutes to get the initial data
_air_quality = Sensors.AirQuality()

# Main outer loop
while True:

    print(str(datetime.now()))
    print('Measuring rain precipitation for {0:g} minutes(s)...'.format(rain_interval / 60))
    # _rainfall.reset_rainfall()
    # Loop for rainfall (longer period)
    rain_start_time = time.time()
    while time.time() - rain_start_time <= rain_interval:
        # Report rain
        rainfall = _rainfall.value
        # print("Rain: " + str(rainfall))

        start_time = time.time()
        # Inner loop for remaining sensors (short period)
        while time.time() - start_time <= interval:
            speed.reset_wind()
            time.sleep(interval)

            # Report wind speed
            final_speed = speed.calculate_speed(interval)
            store_speeds.append(final_speed)

            _wind_gust = max(store_speeds)
            wind_gust = '{:.2f}'.format(_wind_gust)
            _wind_speed = statistics.mean(store_speeds)
            wind_speed = '{:.2f}'.format(_wind_speed)

            # print("Wind speed: {:.2f} km/h".format(float(wind_speed)))
            # print("Wind gust: {:.2f} km/h".format(float(wind_gust)))

            # Report wind direction
            _wind_direction = Sensors.WindDirection(NORTH)
            wind_direction = '{:.2f}'.format(_wind_direction.get_value())
            # print("Wind heading: {} degrees".format(wind_direction))

            # Report ground temperature
            _ground_temperature = Sensors.TemperatureProbe()
            ground_temperature = '{:.2f}'.format(_ground_temperature.read_temp())
            # print("Ground temperature: {:.2f} °C".format(ground_temperature))
            # print("Ground temperature: {} °C".format(ground_temperature))

            # Report ambient temperature, pressure and humidity
            _ambient_temperature.refresh()
            ambient_temperature = '{:.2f}'.format(_ambient_temperature.value)
            # print("Ambient temperature: {} °C".format(ambient_temperature))

            _pressure.refresh()
            pressure = '{:.2f}'.format(_pressure.value)
            # print("Pressure: {} hPa".format(pressure))

            _humidity.refresh()
            humidity = '{:.2f}'.format(_humidity.value)
            # print("Humidity: {} %RH".format(humidity))

            # Report air quality results
            air_quality = '{:.2f}'.format(_air_quality.score())
            gas_resistance = '{:.2f}'.format(_air_quality.gas())
            # print("Air quality: {:.2f} %".format(float(air_quality)))
            # print("Gas resistance: {} Ohms".format(gas_resistance))

            db = WeatherDatabase()

            db.insert(
                ambient_temperature,
                ground_temperature,
                humidity,
                pressure,
                rainfall,
                wind_speed,
                wind_gust,
                wind_direction,
                air_quality,
                gas_resistance)

            db.get_last_result()
