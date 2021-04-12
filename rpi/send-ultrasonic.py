#Libraries
from pickle import dumps
from socket import *
import RPi.GPIO as GPIO
import time

#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)

#GPIO pins setup
#TRIG
REAR_TRIG = 20
FRONT_TRIG = 16
FRONT_RIGHT_TRIG = 13
FRONT_LEFT_TRIG = 12
#ECHO
REAR_ECHO = 26
FRONT_ECHO = 19
FRONT_RIGHT_ECHO = 6
FRONT_LEFT_ECHO = 5

TRIG_PINS = [FRONT_TRIG, FRONT_RIGHT_TRIG, FRONT_LEFT_TRIG, REAR_TRIG]
ECHO_PINS = [FRONT_ECHO, FRONT_RIGHT_ECHO, FRONT_LEFT_ECHO, REAR_ECHO]
#set GPIO direction (IN / OUT)
for pin in range(4):
    GPIO.setup(TRIG_PINS[pin], GPIO.OUT)
    GPIO.setup(ECHO_PINS[pin], GPIO.IN)

def distance(TRIG, ECHO):
    """
    General Purpose Ultrasonic Distance Retriever
    Triggers the passed TRIG Pin
    Records return time of the signal using ECHO
    returns distance in cm
    """
    #Power TRIG and stop after 0.01ms
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    startTime = time.time()
    stopTime = time.time()

    # save StartTime
    while GPIO.input(ECHO) == 0:
        startTime = time.time()

    # save time of arrival
    while GPIO.input(ECHO) == 1:
        stopTime = time.time()

    #signal time travelled
    timeElapsed = stopTime - startTime
    # distance formula
    # /2 to return displacement
    distance = (timeElapsed * 34300) / 2

    return distance

client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect(('192.168.1.74', 6666))

distance_data = {
    "Front"      : -1,
    "Front-Right": -1,
    "Front-Left" : -1,
    "Rear"       : -1,
}
dict_keys = list(distance_data.keys())

if __name__ == '__main__':
    try:
        while True:
            for pin in range(4):
                distance_data[dict_keys[pin]] = distance(TRIG_PINS[pin], ECHO_PINS[pin])
            data = dumps(distance_data)
            client_socket.send(data)
            time.sleep(0.5)

        # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        print("Server stopped")
        GPIO.cleanup()
    finally:
        GPIO.cleanup()