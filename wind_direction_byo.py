import math
import time

from gpiozero import MCP3008

NORTH = 80  # type: int

adc = MCP3008(channel=0)
rain_count = 0
values = []
volts = {0.4: 0.0,
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


def get_average(angles):
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

    return 0.0 if average == 360 else average


def get_value(length=5):
    data = []
    print("Measuring wind direction for %d seconds..." % length)
    start_time = time.time()

    while time.time() - start_time <= length:
        wind = round(adc.value * 3.3, 1)
        if wind not in volts:  # keep only good measurements
            # print('unknown value ' + str(wind))
            continue
        else:
            data.append(volts[wind])

    return get_average(data)


def get_direction(value):

    angle = int(value)
    if angle in range(0, 45):
        return "N"
    elif angle in range(46, 90):
        return "NE"

    return 0


while True:
    direction = (get_value() - NORTH)  # type: float
    print(direction)
    print(get_direction(direction))
    # wind = round(adc.value * 3.3, 1)
    # if wind not in volts:
    #     print('unknown value ' + str(wind) + ' ' + str(volts[wind]))
    # else:
    #     print('found ' + str(wind) + ' ' + str(volts[wind]))