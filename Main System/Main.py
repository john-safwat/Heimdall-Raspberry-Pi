import RPi.GPIO as GPIO
import time

GPIO.cleanup()

# setup the GPIO Numbering Mode To Board (Position of the Pin on The Board)
GPIO.setmode(GPIO.BOARD)

# set the pins for the ultrasonic sensor (Trigger Pin Out & Echo Pin In)
trigPin = 16
echoPin = 18
GPIO.setup(trigPin, GPIO.OUT)
GPIO.setup(echoPin, GPIO.IN)

# set the PIR sensor input Pin to pin 12 
pirInputPin = 12
GPIO.setup(pirInputPin, GPIO.IN)
time.sleep(10)

# set the Magnet Door Lock Pin
magnetPin = 11
GPIO.setup(magnetPin, GPIO.IN)

# set the indicator LEDs pins
firstGreenLedPin = 7
secondGreenLedPin = 3
redLedPin = 5
GPIO.setup(firstGreenLedPin, GPIO.OUT)
GPIO.setup(secondGreenLedPin, GPIO.OUT)
GPIO.setup(redLedPin, GPIO.OUT)


# function to call the ultrasonic sensor
def ultraSonicSensor():
    # send the signals from the trigger pin
    # set the trigPin by 0 for 2 Micro Second (E-6 refers to Micro Second)
    GPIO.output(trigPin, 0)
    time.sleep(2E-6)
    # set the trigPin by 1 for 10 Micro Second (E-6 refers to Micro Second)
    GPIO.output(trigPin, 1)
    time.sleep(10E-6)
    # set the trigPin by 0 again
    GPIO.output(trigPin, 0)

    # count the time between the sending and receiving the signal
    # wait while the reading from echoPin = 0
    while GPIO.input(echoPin) == 0:
        pass
    echoStartTime = time.time()  # read the start time

    # wait while the reading from echoPin = 1
    while GPIO.input(echoPin) == 1:
        pass
    echoStopTime = time.time()  # read the stop time

    ptt = echoStopTime - echoStartTime  # calculate the ping travel time

    distance = round(343 * ptt / 2, 3)  # Calculate the distance
    return distance


# function to call the PIR sensor
def pirSensor():
    # read the input from the output pin in PIR sensor 
    motion = GPIO.input(pirInputPin)
    return motion


def magnetSensor():
    opened = GPIO.input(magnetPin)
    return opened


# define the main function (The Entry Point of the program)
# in this function it will call all sensors function  and handle the logic calling
def main():
    try:
        while True:
            distance = ultraSonicSensor()
            motion = pirSensor()
            opened = magnetSensor()

            if distance > 1 and motion == 0:
                GPIO.output(firstGreenLedPin, 0)
                GPIO.output(secondGreenLedPin, 0)
                GPIO.output(redLedPin, 1)
            elif distance > 1 and motion == 1:
                GPIO.output(firstGreenLedPin, 0)
                GPIO.output(secondGreenLedPin, 1)
                GPIO.output(redLedPin, 1)
            elif distance <= 1 and motion == 0:
                GPIO.output(firstGreenLedPin, 1)
                GPIO.output(secondGreenLedPin, 0)
                GPIO.output(redLedPin, 1)
            else:
                GPIO.output(firstGreenLedPin, 1)
                GPIO.output(secondGreenLedPin, 1)
                GPIO.output(redLedPin, 0)

            time.sleep(0.2)
    except KeyboardInterrupt():
        GPIO.output(secondGreenLedPin, 0)
        GPIO.cleanup()
        print("GPIO is Good To Go")


if __name__ == '__main__':
    main()