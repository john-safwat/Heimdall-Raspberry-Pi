import RPi.GPIO as GPIO
from time import sleep, time
from kplib import Keypad

GPIO.cleanup()

# set up the GPIO Numbering Mode To Board (Position of the Pin on The Board)
GPIO.setmode(GPIO.BOARD)

# set the pins for the ultrasonic sensor (Trigger Pin Out & Echo Pin In)
trigPin = 16
echoPin = 18
GPIO.setup(trigPin, GPIO.OUT)
GPIO.setup(echoPin, GPIO.IN)

# set the PIR sensor input Pin to pin 12 
pirInputPin = 12
GPIO.setup(pirInputPin, GPIO.IN)
sleep(10)

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

# set the buzzer pin
buzzer = 13
GPIO.setup(buzzer, GPIO.OUT)

# set the IR sensor pin
irSensor = 15
GPIO.setup(irSensor, GPIO.IN)


# function to call the ultrasonic sensor
def ultra_sonic_sensor():
    # send the signals from the trigger pin
    # set the trigPin by 0 for 2 Micro Second (E-6 refers to Micro Second)
    GPIO.output(trigPin, 0)
    sleep(2E-6)
    # set the trigPin by 1 for 10 Micro Second (E-6 refers to Micro Second)
    GPIO.output(trigPin, 1)
    sleep(10E-6)
    # set the trigPin by 0 again
    GPIO.output(trigPin, 0)

    # count the time between the sending and receiving the signal
    # wait while the reading from echoPin = 0
    while GPIO.input(echoPin) == 0:
        pass
    echo_start_time = time()  # read the start time

    # wait while the reading from echoPin = 1
    while GPIO.input(echoPin) == 1:
        pass
    echo_stop_time = time()  # read the stop time

    ptt = echo_stop_time - echo_start_time  # calculate the ping travel time

    distance = round(343 * ptt / 2, 3)  # Calculate the distance
    return distance


# function to call the PIR sensor
def pir_sensor():
    # read the input from the output pin in PIR sensor 
    motion = GPIO.input(pirInputPin)
    return motion


# function to call the magnet sensor
def magnet_sensor():
    opened = GPIO.input(magnetPin)
    return opened


# function to call the buzzer
def set_buzzer():
    GPIO.output(buzzer, GPIO.HIGH)
    sleep(0.5)
    GPIO.output(buzzer, GPIO.LOW)
    sleep(0.5)


def ir_sensor():
    ir = GPIO.input(irSensor)
    return ir


# define the main function (The Entry Point of the program)
# in this function it will call all sensor's function and handle the logic calling
def main():
    try:
        while True:
            distance = ultra_sonic_sensor()
            motion = pir_sensor()
            opened = magnet_sensor()
            if opened == 1:
                while True:
                    set_buzzer()
                    if magnet_sensor() == 0:
                        break
                    sleep(0.5)
            my_keypad = Keypad()
            myString = my_keypad.read_keypad()
            print(myString)
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

            sleep(0.2)
    except KeyboardInterrupt():
        GPIO.output(secondGreenLedPin, 0)
        GPIO.cleanup()
        print("GPIO is Good To Go")


if __name__ == '__main__':
    main()
