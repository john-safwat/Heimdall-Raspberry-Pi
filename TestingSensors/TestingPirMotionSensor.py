import RPi.GPIO as GPIO
from time import sleep

motionPin = 12
GPIO.setmode(GPIO.BOARD)
GPIO.setup(motionPin,GPIO.IN)
sleep(10)

try:
    while True:
        motion = GPIO.input(motionPin)
        print(motion)
        sleep(0.1)
except KeyboardInterrupt:
    GPIO.cleanup()
    print('GPIO Good to Go')