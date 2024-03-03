import RPi.GPIO as GPIO
from time import sleep, time
from picamera2 import Picamera2
from firebase_admin import db
import pyrebase
import cv2
import random
import string
import datetime
import threading

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
y1: int = 0
y2: int = 0
x1: int = 640
x2: int = 0

# configurations Variables
alert_counter = 600
opened: bool = True
login_error_message: str = ""
image_uploading_error: str = ""
updating_state_error: str = ""

# setup GPIO pins
GPIO.setup(trig_pin, GPIO.OUT)
GPIO.setup(echo_pin, GPIO.IN)
GPIO.setup(pir_input_pin, GPIO.IN)
sleep(10)
GPIO.setup(magnet_pin, GPIO.IN)
GPIO.setup(ir_pin, GPIO.IN)
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

# Load pre-trained face detector
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')


def random_string_generator():
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(20))


# login function
def login():
    global token, lock_id, login_error_message
    try:
        print("Login")
        with open('auth_data.txt', 'r') as file:
            email_and_password = file.read().split("\n")
            print(email_and_password)
            email = email_and_password[0]
            lock_password = email_and_password[1]
            login_user = pyrebase_auth.sign_in_with_email_and_password(email, lock_password)
            print("Successfully logged in!")
            lock_id = login_user['localId']
            token = login_user["idToken"]
            print(lock_id)
    except Exception as e:
        login_error_message = str(e)


def setup_lock_configuration():
    global password, y1, y2, x1, x2
    my_stream = pyrebase_database.child(f"Locks/{lock_id}").stream(stream_handler)
    lock_document = pyrebase_database.child(f"Locks/{lock_id}/password").get(token)
    password = lock_document.val()
    y1_coordinate = pyrebase_database.child(f"Locks/{lock_id}/y1_value").get(token)
    y1 = y1_coordinate.val()
    y2_coordinate = pyrebase_database.child(f"Locks/{lock_id}/y2_value").get(token)
    y2 = y2_coordinate.val()
    x1_coordinate = pyrebase_database.child(f"Locks/{lock_id}/x1_value").get(token)
    x1 = x1_coordinate.val()
    x2_coordinate = pyrebase_database.child(f"Locks/{lock_id}/x2_value").get(token)
    x2 = x2_coordinate.val()


# stream handler function (listener)
def stream_handler(message):
    global password, y1, y2, x1, x2
    if message["path"] == "/opened":
        if message["data"]:
            open_door()
        else:
            close_door()
    if message["path"] == "/password":
        password = message["data"]
    if message["path"] == "/y1_value":
        y1 = message["data"]
    if message["path"] == "/y2_value":
        y2 = message["data"]
    if message["path"] == "/x1_value":
        x1 = message["data"]
    if message["path"] == "/x2_value":
        x2 = message["data"]
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
    magnet_read = GPIO.input(magnet_pin)
    return magnet_read


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
    global opened, updating_state_error
    if not opened:
        GPIO.output(lock, 1)
        try:
            pyrebase_database.child(f"Locks/{lock_id}/opened").set(True)
        except Exception as e:
            updating_state_error = str(e)

        sleep(2)
        opened = not opened


# function to close the door
def close_door():
    global opened, updating_state_error
    if opened:
        GPIO.output(lock, 0)
        try:
            pyrebase_database.child(f"Locks/{lock_id}/opened").set(False)
        except Exception as e:
            updating_state_error = str(e)
        opened = not opened


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
            # Capture image using cv2.imWrite()
            cv2.imwrite(f'images/{image_name}.jpg', frame)
            print("face detected")

    cv2.destroyAllWindows()
    return images


def line_intersects_rectangle(p1, p2, r1, r2, c1, c2):
    """
    Checks if the line segment defined by points p1 and p2 intersects with the rectangle defined by coordinates (r1,
    c1), (r2, c1), (r2, c2), and (r1, c2).

    Args:
        p1: Tuple (x, y) of the starting point of the line segment.
        p2: Tuple (x, y) of the ending point of the line segment.
        r1: Float, x-coordinate of the leftmost point of the rectangle.
        r2: Float, x-coordinate of the rightmost point of the rectangle.
        c1: Float, y-coordinate of the topmost point of the rectangle.
        c2: Float, y-coordinate of the bottommost point of the rectangle.

    Returns:
        True if the line segment intersects the rectangle, False otherwise.
    """

    # Check if the line segment is completely outside the rectangle
    if (p1[0] < r1 and p2[0] < r1) or (p1[0] > r2 and p2[0] > r2) or (p1[1] < c2 and p2[1] < c2) or (
            p1[1] > c1 and p2[1] > c1):
        return False

    # Check for intersection with each side of the rectangle
    for x in [r1, r2]:
        if line_intersects_line(p1, p2, (x, c1), (x, c2)):
            return True

    for y in [c1, c2]:
        if line_intersects_line(p1, p2, (r1, y), (r2, y)):
            return True

    return False


def line_intersects_line(p1, p2, q1, q2):
    """
    Checks if two line segments defined by points p1, p2 and q1, q2 intersect.

    Args:
        p1: Tuple (x, y) of the starting point of the first line segment.
        p2: Tuple (x, y) of the ending point of the first line segment.
        q1: Tuple (x, y) of the starting point of the second line segment.
        q2: Tuple (x, y) of the ending point of the second line segment.

    Returns:
        True if the line segments intersect, False otherwise.
    """

    # Calculate the denominator to avoid division by zero
    denominator = (p2[0] - p1[0]) * (q2[1] - q1[1]) - (p2[1] - p1[1]) * (q2[0] - q1[0])

    # Check if lines are parallel
    if denominator == 0:
        return False

    # Calculate the intersection point parameters
    t = ((q2[0] - q1[0]) * (p1[1] - q1[1]) + (q2[1] - q1[1]) * (q1[0] - p1[0])) / denominator
    u = ((p2[0] - p1[0]) * (p1[1] - q1[1]) + (p2[1] - p1[1]) * (q1[0] - p1[0])) / denominator

    # Check if the intersection point is within the line segments
    return 0 <= t <= 1 and 0 <= u <= 1


def uploadImages(images):
    urls = []
    for i in range(len(images)):
        pyrebase_storage.child(f"captures/{images[i]}.jpg").put(f'images/{images[i]}.jpg')
        url = pyrebase_storage.child(f"captures/{images[i]}.jpg").get_url(token)
        urls.append(url)
    print(urls)
    return urls


# define the main function (The Entry Point of the program)
# in this function it will call all sensor's function and handle the logic calling
def main():
    global alert_counter
    # define the password
    user_password = ""
    last_Key = ""
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
            if (ultra_sonic < 1) or pirRead or irRead:
                if alert_counter > 400:
                    images = captureImages()
                    if len(images) != 0:
                        alert_counter = 0
                        thread = threading.Thread(target=uploadImages, args=(images,))
                        thread.start()
                        print(urls)

            # qr_code_scanning()
            frame = piCam.capture_array()
            # Convert to grayscale for efficiency
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # Detect faces
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)

            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (252, 207, 32), 1)
                key = cv2.waitKey(1) & 0xFF
                if line_intersects_rectangle((x1, y1), (x2, y2), x, (x + w), y, (y + h)):
                    print("caught one")

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
    setup_lock_configuration()
    main()
