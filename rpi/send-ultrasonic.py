##Failing somewhere

import RPi.GPIO as GPIO
import time
#import sockets

GPIO.setmode(GPIO.BCM)

right_trigger = 26
right_echo = 19
left_trigger = 20
left_echo = 21

#GPIO.cleanup()
GPIO.setup(left_trigger, GPIO.OUT)
GPIO.setup(left_echo, GPIO.IN)
GPIO.setup(right_trigger, GPIO.OUT)
GPIO.setup(right_echo, GPIO.IN)


def distance_left():
    GPIO.output(left_trigger, True)

    time.sleep(0.00001)
    GPIO.output(left_trigger, False)

    start_time = time.time()
    stop_time = time.time()

    while GPIO.input(left_echo) == 0:
        start_time = time.time()

    while GPIO.input(left_echo) == 1:
        stop_time = time.time()

    time_elapsed = stop_time - start_time

    distance = (time_elapsed * 34300) / 2
    return distance


def distance_right():
    GPIO.output(right_trigger, True)

    time.sleep(0.00001)
    GPIO.output(right_trigger, False)

    start_time = time.time()
    stop_time = time.time()

    while GPIO.input(right_echo) == 0:
        start_time = time.time()

    while GPIO.input(right_echo) == 1:
        stop_time = time.time()

    time_elapsed = stop_time - start_time

    distance = (time_elapsed * 34300) / 2
    return distance


if '__name__' == '__main__':

    try:
        while True:
            left_obs, right_obs = distance_left(), distance_right()
            print(';jdosvib',left_obs, right_obs)

    except KeyboardInterrupt:
        print("Program ended by KeyboardInterrupt")
        GPIO.cleanup()

