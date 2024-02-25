import RPi.GPIO as GPIO
from time import sleep, time
from picamera2 import Picamera2
from firebase_admin import db
import pyrebase
import cv2
import random
import string
import datetime

GPIO.cleanup()

GPIO.setwarnings(False)
# set up the GPIO Numbering Mode To Board (Position of the Pin on The Board)
GPIO.setmode(GPIO.BOARD)

firebase_config = {
    "apiKey": "AIzaSyD7BJiwIa7J2llFnmYe-eHTtKJi11gnBxc",
    "authDomain": "heimdall-5aecb.firebaseapp.com",
    "databaseURL": "https://heimdall-5aecb-default-rtdb.firebaseio.com",
    "projectId": "heimdall-5aecb",
    "storageBucket": "heimdall-5aecb.appspot.com",
    "messagingSenderId": "162564554099",
    "appId": "1:162564554099:web:7d8d43779925e659d1d906",
    "measurementId": "G-YJY39SDG6Z",
    "serviceAccount": "heimdall.json",
}

# initialize pyrebase
pyrebase_firebase = pyrebase.initialize_app(firebase_config)
# initialize pyrebase auth
pyrebase_auth = pyrebase_firebase.auth()
# initialize pyrebase database
pyrebase_database = pyrebase_firebase.database()
# initialize pyrebase storage
pyrebase_storage = pyrebase_firebase.storage()

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

# the local data
lock_id: str = "id"
token: str = "token"
password: str = "password"
last_capture_time = datetime.datetime.now()

# configurations Variables
alert_counter = 600

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
# camera setup
piCam = Picamera2()
# set the resolution of the camera
piCam.preview_configuration.main.size = (640, 360)
piCam.preview_configuration.main.format = "RGB888"  # we use RGB888 because opencv uses BGR
piCam.preview_configuration.align()
piCam.configure("preview")
piCam.start()

# set up camera object
cap = cv2.VideoCapture(0)
# Load pre-trained face detector
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
# QR code detection object
detector = cv2.QRCodeDetector()


def random_string_generator():
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(20))


# login function
def login():
    global token
    global lock_id

    print("Login")
    # email = input("enter your email : ")
    # loc_password = input("enter your password : ")
    email = "1994640082@heimdall.com"
    loc_password = "123123123"
    login_user = pyrebase_auth.sign_in_with_email_and_password(email, loc_password)
    print("Successfully logged in!")
    lock_id = login_user['localId']
    token = login_user["idToken"]
    print(lock_id)


# stream handler function (listener)
def stream_handler(message):
    global password
    if message["path"] == "/opened":
        if message["data"]:
            open_door()
        else:
            close_door()
    if message["path"] == "/password":
        password = message["data"]
    print("-------------------")
    print(message["event"])  # put
    print(message["path"])  # /uid
    print(message["data"])  # true or false


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
    pyrebase_database.child(f"Locks/{lock_id}/opened").set(True)
    sleep(2)


# function to close the door
def close_door():
    GPIO.output(lock, 0)
    pyrebase_database.child(f"Locks/{lock_id}/opened").set(False)


# function to read each row and each column
def read_keypad(last_key, user_password):
    key = ""
    # loop on the 4 rows and columns to get the input
    for i in range(0, 3):
        GPIO.output(rows[i], GPIO.LOW)
        for j in range(0, 3):
            if GPIO.input(cols[j]) == GPIO.LOW:
                key = characters[i][j]
        GPIO.output(rows[i], GPIO.HIGH)
    # check if is equal to the last pressed key
    if key != last_key:
        last_key = key
        user_password = user_password + key
    return user_password, last_key


# function to validate on password
def password_validation(user_password: str):
    global password
    if len(user_password) == len(password):
        if user_password == password:
            open_door()
            user_password = ""
        else:
            set_buzzer()
            set_buzzer()
            set_buzzer()
            user_password = ""
    elif len(user_password) > len(password):
        user_password = ""

    return user_password


def captureImages():
    images = []
    for i in range(30):
        frame = piCam.capture_array()
        # Convert to grayscale for efficiency
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Detect faces
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (252, 207, 32), 1)
            key = cv2.waitKey(1) & 0xFF
            image_name = random_string_generator()
            images.append(image_name)
            # Capture image using cv2.imwrite()
            cv2.imwrite(f'images/{image_name}.jpg', frame)

        # Display frame
        cv2.imshow('User Image', frame)
    # Release resources
    cv2.destroyAllWindows()
    return images


def uploadImages(images):
    global alert_counter
    urls = []
    for i in range(len(images)):
        pyrebase_storage.child(f"taked/{images[i]}.jpg").put(f'images/{images[i]}.jpg')
        url = pyrebase_storage.child(f"taked/{images[i]}.jpg").get_url(token)
        urls.append(url)
    print(urls)
    alert_counter = 0
    return urls


def qr_code_scanning():
    try:
        _, img = piCam.capture_array()
        # detect and decode
        data, bbox, _ = detector.detectAndDecode(img)
        # check if there is a QRCode in the image
        if data:
            print(data)
        # Below will display the live camera feed to the Desktop on Raspberry Pi OS preview
        cv2.imshow("code detector", img)
        # When the code is stopped the below closes all the applications/windows that the above has created
        cap.release()
        cv2.destroyAllWindows()
    except Exception as e:
        print("Error reading frame:", e)


# define the main function (The Entry Point of the program)
# in this function it will call all sensor's function and handle the logic calling
def main():
    global last_capture_time
    global alert_counter
    # define the password
    user_password = ""
    last_Key = ""
    images = []
    urls = []
    try:
        while True:
            # get the reads from the sensors and the keypad
            user_password, last_Key = read_keypad(last_Key, user_password)
            user_password = password_validation(user_password)
            print(user_password)
            ultra_sonic = ultra_sonic_sensor()
            irRead = not ir_sensor()
            pirRead = pir_sensor()
            magnetRead = magnet_sensor()
            print(f"Ultrasonic - {ultra_sonic}")
            print(f"PIR - {pirRead}")
            print(f"IR - {irRead}")
            print(f"Counter - {alert_counter}")

            # change the light state depend on the sensors read
            if (ultra_sonic < 1 and irRead) or (irRead and pirRead) or (ultra_sonic < 1 and pirRead):
                if alert_counter > 400:
                    images = captureImages()
                    urls = uploadImages(images)
                    print(urls)

            qr_code_scanning()

            # if the door is opened the lock is opened
            if not magnetRead:
                close_door()
            else:
                open_door()

            alert_counter += 1
            sleep(0.1)
    except KeyboardInterrupt():
        GPIO.cleanup()
        print("GPIO is Good To Go")


if __name__ == '__main__':
    login()
    my_stream = pyrebase_database.child(f"Locks/{lock_id}").stream(stream_handler)
    lock_document = pyrebase_database.child(f"Locks/{lock_id}/password").get(token)
    password = lock_document.val()
    main()
