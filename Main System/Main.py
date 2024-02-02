import RPi.GPIO as GPIO
from time import sleep, time
from picamera2 import Picamera2

GPIO.cleanup()

GPIO.setwarnings(False)
# set up the GPIO Numbering Mode To Board (Position of the Pin on The Board)
GPIO.setmode(GPIO.BOARD)

# define the variables
# set the pins for the ultrasonic sensor (Trigger Pin Out & Echo Pin In)
trig_pin = 16
echo_pin = 18
# set the PIR sensor input Pin to pin 12
pir_input_pin = 12
# set the Magnet Door Lock Pin
magnet_pin = 11
# set the IR sensor pin
ir_pin = 15
# set the indicator LEDs pins
first_green_led_pin = 3
second_green_led_pin = 5
third_green_led_pin = 7
# set the buzzer pin
buzzer = 13
# setup the lock
lock = 19
# Set the Row Pins
rows = [31, 33, 35, 37]

# Set the Column Pins
cols = [32, 36, 38, 40]

# the characters
characters = [["1", "2", "3", "A"],
              ["4", "5", "6", "B"],
              ["7", "8", "9", "C"],
              ["*", "0", "#", "D"]]

# setup GPIO pins
GPIO.setup(trig_pin, GPIO.OUT)
GPIO.setup(echo_pin, GPIO.IN)
GPIO.setup(pir_input_pin, GPIO.IN)
sleep(10)
GPIO.setup(magnet_pin, GPIO.IN)
GPIO.setup(ir_pin, GPIO.IN)
GPIO.setup(first_green_led_pin, GPIO.OUT)
GPIO.setup(second_green_led_pin, GPIO.OUT)
GPIO.setup(third_green_led_pin, GPIO.OUT)
GPIO.setup(buzzer, GPIO.OUT)
GPIO.setup(lock, GPIO.OUT)
GPIO.setup(rows[0], GPIO.OUT)
GPIO.setup(rows[1], GPIO.OUT)
GPIO.setup(rows[2], GPIO.OUT)
GPIO.setup(rows[3], GPIO.OUT)
GPIO.setup(cols[0], GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(cols[1], GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(cols[2], GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(cols[3], GPIO.IN, pull_up_down=GPIO.PUD_UP)


# function to call the ultrasonic sensor
def ultra_sonic_sensor():
    # send the signals from the trigger pin
    # set the trigPin by 0 for 2 Micro Second (E-6 refers to Micro Second)
    GPIO.output(trig_pin, 0)
    sleep(2E-6)
    # set the trigPin by 1 for 10 Micro Second (E-6 refers to Micro Second)
    GPIO.output(trig_pin, 1)
    sleep(10E-6)
    # set the trigPin by 0 again
    GPIO.output(trig_pin, 0)

    # count the time between the sending and receiving the signal
    # wait while the reading from echoPin = 0
    while GPIO.input(echo_pin) == 0:
        pass
    echo_start_time = time()  # read the start time

    # wait while the reading from echoPin = 1
    while GPIO.input(echo_pin) == 1:
        pass
    echo_stop_time = time()  # read the stop time

    ptt = echo_stop_time - echo_start_time  # calculate the ping travel time

    distance = round(343 * ptt / 2, 3)  # Calculate the distance
    return distance


# function to call the PIR sensor
def pir_sensor():
    # read the input from the output pin in PIR sensor
    motion = GPIO.input(pir_input_pin)
    return motion


# function to call the magnet sensor
def magnet_sensor():
    opened = GPIO.input(magnet_pin)
    return opened


# function to call the ir sensor
def ir_sensor():
    ir = GPIO.input(ir_pin)
    return ir


# function to call the buzzer
def set_buzzer():
    GPIO.output(buzzer, GPIO.HIGH)
    sleep(0.15)
    GPIO.output(buzzer, GPIO.LOW)
    sleep(0.15)


# function to open the door
def open_door():
    GPIO.output(lock, 1)


# function to close the door
def close_door():
    GPIO.output(lock, 0)


# function to read each row and each column
def read_keypad(last_key, password):
    key = ""
    print(last_key == key)
    for i in range(0, 3):
        GPIO.output(rows[i], GPIO.LOW)
        for j in range(0, 3):
            if GPIO.input(cols[j]) == GPIO.LOW:
                key = characters[i][j]
        GPIO.output(rows[i], GPIO.HIGH)

    if key != last_key:
        last_key = key
        password = password + key
    return password, last_key


# function to validate on password
def password_validation(password: str):
    if len(password) == 4:
        if password == "1234":
            open_door()
            password = ""
        else:
            set_buzzer()
            set_buzzer()
            set_buzzer()
            password = ""
    elif len(password) > 4:
        password = ""

    return password


# define the main function (The Entry Point of the program)
# in this function it will call all sensor's function and handle the logic calling
def main():
    # define the password
    password = ""
    last_Key = ""
    try:
        while True:
            # get the reads from the sensors and the keypad
            password, last_Key = read_keypad(last_Key, password)
            password = password_validation(password)
            print(f"the password {password}")
            ultra_sonic = ultra_sonic_sensor()
            irRead = ir_sensor()
            pirRead = pir_sensor()
            magnetRead = magnet_sensor()
            print("---------------------------")

            # change the light state depend on the sensors read
            if ultra_sonic < 0.5:
                GPIO.output(first_green_led_pin, 1)
            else:
                GPIO.output(first_green_led_pin, 0)

            if not irRead:
                GPIO.output(second_green_led_pin, 1)
            else:
                GPIO.output(second_green_led_pin, 0)

            if pirRead:
                GPIO.output(third_green_led_pin, 1)
            else:
                GPIO.output(third_green_led_pin, 0)

            # if the door is opened the lock is opened
            if not magnetRead:
                close_door()
            sleep(0.1)
    except KeyboardInterrupt():
        GPIO.cleanup()
        print("GPIO is Good To Go")


if __name__ == '__main__':
    main()
