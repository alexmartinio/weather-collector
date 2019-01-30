import datetime
import glob
import math
import time

import bme680
from gpiozero import Button, MCP3008


class Sensor:
    __value = 0.0
    __lowest = 0.0
    __highest = 0.0

    def __init__(self):
        self.name = ''
        self.value = 0.0

    @property
    def value(self):
        return self.__value

    @value.getter
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        self.__value = value
        if value is not None:
            if self.value < self.__lowest:
                self.__lowest = self.value
            if self.value > self.__highest:
                self.__highest = self.value

    @property
    def highest(self):
        return self.__highest

    @property
    def lowest(self):
        return self.__lowest


class Rain(Sensor):
    BUCKET_SIZE = 0.2794
    rain_count = 0

    def __init__(self):
        super().__init__()
        __rain_sensor = Button(6)
        __rain_sensor.when_pressed = self.__bucket_tipped

    def __bucket_tipped(self):
        # global rain_count
        self.rain_count += 1
        # rain_count = rain_count + 1
        Sensor.value = self.rain_count * self.BUCKET_SIZE
        self.value = self.rain_count * self.BUCKET_SIZE
        print(datetime.datetime.now())
        print(self.rain_count * self.BUCKET_SIZE)

    def reset_rainfall(self):
        self.rain_count = 0


class WindSpeed(Sensor):
    wind_count = 0  # type: int # Counts how many half-rotations
    radius_cm = 9.0  # Radius of your anemometer

    # Constants
    __ADJUSTMENT = 1.18
    __CM_IN_A_KM = 100000.0
    __SECS_IN_AN_HOUR = 3600

    # __wind_speed_sensor = Button(5)
    __WIND_SPEED_SENSOR = Button(5)

    def __init__(self):
        super().__init__()
        global wind_count
        # wind_count = 0
        self.reset_wind()
        # wind_speed_sensor.when_pressed = self.spin
        # wind_speed_sensor.when_activated = self.spin
        # self.__wind_speed_sensor.when_pressed = self.spin
        # self.__wind_speed_sensor.when_activated = self.spin

        self.__WIND_SPEED_SENSOR.when_pressed = self.spin
        self.__WIND_SPEED_SENSOR.when_activated = self.spin

    # Every half-rotation, add 1 to count
    @staticmethod
    def spin():
        global wind_count
        wind_count = wind_count + 1

    # Calculate the wind speed
    @staticmethod
    def calculate_speed(time_sec):
        global wind_count
        circumference_cm = (2 * math.pi) * WindSpeed.radius_cm
        rotations = wind_count / 2.0

        # Calculate distance travelled by a cup in cm
        dist_km = (circumference_cm * rotations) / WindSpeed.__CM_IN_A_KM

        km_per_sec = dist_km / time_sec
        km_per_hour = km_per_sec * WindSpeed.__SECS_IN_AN_HOUR

        return km_per_hour * WindSpeed.__ADJUSTMENT

    @staticmethod
    def reset_wind():
        global wind_count
        wind_count = 0


class WindDirection(Sensor):
    # Vars and constants
    north = 0
    __ADC = MCP3008(channel=0)
    __VOLTS = {0.4: 0.0,
               1.4: 22.5,
               1.2: 45.0,
               2.8: 67.5,
               2.7: 90.0,
               2.9: 112.5,
               2.2: 135.0,
               2.5: 157.5,
               1.8: 180.0,
               2.0: 202.5,
               0.7: 225.0,
               0.8: 247.5,
               0.1: 270.0,
               0.3: 292.5,
               0.2: 315.0,
               0.6: 337.5}

    def __init__(self, north_heading=0):
        super().__init__()
        # facing 305 is 90
        # 360 - 305 = 55 + 90 = 145 North
        WindDirection.north = north_heading

    @staticmethod
    def __get_average(angles):
        global north
        sin_sum = 0.0
        cos_sum = 0.0

        for angle in angles:
            r = math.radians(angle)
            sin_sum += math.sin(r)
            cos_sum += math.cos(r)

        flen = float(len(angles))
        s = sin_sum / flen
        c = cos_sum / flen
        arc = math.degrees(math.atan(s / c))
        average = 0.0

        if s > 0 and c > 0:
            average = arc
        elif c < 0:
            average = arc + 180
        elif s < 0 < c:
            average = arc + 360

        adjusted_direction = WindDirection.north + average
        # if adjusted_direction > 360: adjusted_direction = adjusted_direction - 360
        if adjusted_direction > 360:
            fixed_direction = adjusted_direction - 360
            print('Fixed direction: {:.2f}'.format(fixed_direction))
            print('Adjusted direction: {:.2f}'.format(adjusted_direction))
        return 0.0 if average == 360 else average

    @staticmethod
    def get_value(length=5):
        data = []
        # print("Measuring wind direction for %d seconds..." % length)
        start_time = time.time()
        while time.time() - start_time <= length:
            wind = round(WindDirection.__ADC.value * 3.3, 1)
            if wind not in WindDirection.__VOLTS:  # keep only good measurements
                # print('unknown value ' + str(wind))
                continue
            else:
                data.append(WindDirection.__VOLTS[wind])
        return WindDirection.__get_average(data)


class TemperatureProbe(Sensor):

    # Vars and constants

    def __init__(self):
        super().__init__()
        self.device_file = glob.glob("/sys/bus/w1/devices/28*")[0] + "/w1_slave"

    def read_temp_raw(self):
        f = open(self.device_file, "r")
        lines = f.readlines()
        f.close()
        return lines

    @staticmethod
    def __crc_check(lines):
        return lines[0].strip()[-3:] == "YES"

    def read_temp(self):
        temp_c = -255
        attempts = 0

        lines = self.read_temp_raw()
        success = self.__crc_check(lines)

        while not success and attempts < 3:
            time.sleep(.2)
            lines = self.read_temp_raw()
            success = self.__crc_check(lines)
            attempts += 1

        if success:
            temp_line = lines[1]
            equal_pos = temp_line.find("t=")
            if equal_pos != -1:
                temp_string = temp_line[equal_pos + 2:]
                temp_c = float(temp_string) / 1000.0

        return temp_c


class AmbientTemperature(Sensor):
    # Vars and constants
    try:
        sensor = bme680.BME680(bme680.constants.I2C_ADDR_PRIMARY)
    except IOError:
        sensor = bme680.BME680(bme680.constants.I2C_ADDR_SECONDARY)

    def __init__(self):
        super().__init__()
        self.sensor.set_temperature_oversample(bme680.constants.OS_8X)
        self.sensor.set_filter(bme680.constants.FILTER_SIZE_3)

    def refresh(self):
        self.value = None
        while not self.value:
            if self.sensor.get_sensor_data():
                self.value = self.sensor.data.temperature


class Pressure(Sensor):
    # Vars and constants
    try:
        sensor = bme680.BME680(bme680.constants.I2C_ADDR_PRIMARY)
    except IOError:
        sensor = bme680.BME680(bme680.constants.I2C_ADDR_SECONDARY)

    def __init__(self):
        super().__init__()
        self.sensor.set_pressure_oversample(bme680.constants.OS_4X)
        self.sensor.set_filter(bme680.constants.FILTER_SIZE_3)
        self.value = None

    def refresh(self):
        self.value = None
        while not self.value:
            if self.sensor.get_sensor_data():
                self.value = self.sensor.data.pressure


class Humidity(Sensor):
    # Vars and constants
    try:
        sensor = bme680.BME680(bme680.constants.I2C_ADDR_PRIMARY)
    except IOError:
        sensor = bme680.BME680(bme680.constants.I2C_ADDR_SECONDARY)

    def __init__(self):
        super().__init__()
        self.sensor.set_humidity_oversample(bme680.constants.OS_2X)
        self.sensor.set_filter(bme680.constants.FILTER_SIZE_3)
        self.value = None

    def refresh(self):
        self.value = None
        while not self.value:
            if self.sensor.get_sensor_data():
                self.value = self.sensor.data.humidity


class AirQuality(Sensor):
    # Vars and constants
    # Set the humidity baseline to 40%, an optimal indoor humidity. SHOULD BE OUTDOORS!
    hum_baseline = 60.0
    # This sets the balance between humidity and gas reading in the
    # calculation of air_quality_score (25:75, humidity:gas)
    hum_weighting = 0.25
    gas_baseline = 0

    burn_in_data = []

    try:
        sensor = bme680.BME680(bme680.constants.I2C_ADDR_PRIMARY)
    except IOError:
        sensor = bme680.BME680(bme680.constants.I2C_ADDR_SECONDARY)

    def __init__(self):
        super().__init__()
        self.sensor.set_humidity_oversample(bme680.constants.OS_2X)
        self.sensor.set_filter(bme680.constants.FILTER_SIZE_3)

        # These oversampling settings can be tweaked to
        # change the balance between accuracy and noise in
        # the data.

        self.sensor.set_humidity_oversample(bme680.constants.OS_2X)
        self.sensor.set_pressure_oversample(bme680.constants.OS_4X)
        self.sensor.set_temperature_oversample(bme680.constants.OS_8X)
        self.sensor.set_filter(bme680.constants.FILTER_SIZE_3)
        self.sensor.set_gas_status(bme680.constants.ENABLE_GAS_MEAS)

        self.sensor.set_gas_heater_temperature(320)
        self.sensor.set_gas_heater_duration(150)
        self.sensor.select_gas_heater_profile(0)

        # start_time and curr_time ensure that the
        # burn_in_time (in seconds) is kept track of.

        start_time = time.time()
        curr_time = time.time()
        # burn_in_time = 300
        burn_in_time = 10

        # burn_in_data = []

        try:
            # Collect gas resistance burn-in values, then use the average
            # of the last 50 values to set the upper limit for calculating
            # gas_baseline.
            print('Collecting gas resistance burn-in data for {0:g} minute(s)...'.format(burn_in_time / 60))
            while curr_time - start_time < burn_in_time:
                curr_time = time.time()
                if self.sensor.get_sensor_data() and self.sensor.data.heat_stable:
                    gas = self.sensor.data.gas_resistance
                    self.burn_in_data.append(gas)
                    # print('Gas: {0} Ohms'.format(gas))
                    time.sleep(1)
                print(str(len(self.burn_in_data)))
            self.gas_baseline = sum(self.burn_in_data[-50:]) / 50.0

            print('Gas baseline: {0} Ohms, humidity baseline: {1:.2f} %RH\n'.format(
                self.gas_baseline,
                self.hum_baseline))

        except KeyboardInterrupt:
            pass

    def score(self):
        hum_baseline = self.hum_baseline
        hum_weighting = self.hum_weighting
        gas_baseline = self.gas_baseline

        air_quality_score = None
        while air_quality_score is None:
            if self.sensor.get_sensor_data() and self.sensor.data.heat_stable:
                gas = self.sensor.data.gas_resistance

                # Add to the burn in data, but only keep last 500 results
                # print(str(len(self.burn_in_data)))
                if len(self.burn_in_data) >= 500:
                    del (self.burn_in_data[0])
                self.burn_in_data.append(gas)
                self.gas_baseline = sum(self.burn_in_data[-50:]) / 50.0

                gas_offset = gas_baseline - gas

                hum = self.sensor.data.humidity
                hum_offset = hum - hum_baseline

                # Calculate hum_score as the distance from the hum_baseline.
                if hum_offset > 0:
                    hum_score = (100 - hum_baseline - hum_offset)
                    hum_score /= (100 - hum_baseline)
                    hum_score *= (hum_weighting * 100)

                else:
                    hum_score = (hum_baseline + hum_offset)
                    hum_score /= hum_baseline
                    hum_score *= (hum_weighting * 100)

                # Calculate gas_score as the distance from the gas_baseline.
                if gas_offset > 0:
                    gas_score = (gas / gas_baseline)
                    gas_score *= (100 - (hum_weighting * 100))

                else:
                    gas_score = 100 - (hum_weighting * 100)

                # Calculate air_quality_score.
                air_quality_score = hum_score + gas_score

                # print('Gas baseline: {0} Ohms, humidity baseline: {1:.2f} %RH\n'.format(
                #    self.gas_baseline,
                #    self.hum_baseline))

                return air_quality_score

    def gas(self):
        gas_resistance = None
        while gas_resistance is None:
            if self.sensor.get_sensor_data() and self.sensor.data.heat_stable:
                gas_resistance = self.sensor.data.gas_resistance
                return gas_resistance
