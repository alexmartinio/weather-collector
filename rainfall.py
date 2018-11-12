from gpiozero import Button

BUCKET_SIZE = 0.2794
rain_count = 0


def bucket_tipped():
    global rain_count
    rain_count = rain_count + 1
    print(rain_count * BUCKET_SIZE)


def reset_rainfall():
    global rain_count
    rain_count = 0


rain_sensor = Button(6)

while True:
    rain_sensor.when_pressed = bucket_tipped

rainfall = rain_count * BUCKET_SIZE
reset_rainfall()

