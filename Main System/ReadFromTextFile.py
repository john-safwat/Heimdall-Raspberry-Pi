import pyrebase
import cv2
import random
import string

token: str = ""
lock_id: str = ""
y1: int = 0
y2: int = 0
x1: int = 640
x2: int = 0

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

# configurations Variables
alert_counter = 600
opened: bool = True
password: str = ""
login_error_message: str = ""
image_uploading_error: str = ""
updating_state_error: str = ""

# Initialize camera
cap = cv2.VideoCapture(0)  # Change number for different camera indices

# Load pre-trained face detector
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')


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
    y1 = float(y1_coordinate.val())
    y2_coordinate = pyrebase_database.child(f"Locks/{lock_id}/y2_value").get(token)
    y2 = float(y2_coordinate.val())
    x1_coordinate = pyrebase_database.child(f"Locks/{lock_id}/x1_value").get(token)
    x1 = float(x1_coordinate.val())
    x2_coordinate = pyrebase_database.child(f"Locks/{lock_id}/x2_value").get(token)
    x2 = float(x2_coordinate.val())


def stream_handler(message):
    global password, y1, y2, x1, x2
    if message["path"] == "/opened":
        if message["data"]:
            print("Opened")
        else:
            print("Closed")
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


def line_intersects_rectangle(p1, p2, r1, r2, c1, c2):
    """
    Checks if the line segment defined by points p1 and p2 intersects with the rectangle defined by coordinates (r1, c1), (r2, c1), (r2, c2), and (r1, c2).

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

    # Check if any coordinate is invalid (e.g., not a number)
    if not all(isinstance(x, (int, float)) for x in [p1[0], p1[1], p2[0], p2[1], r1, r2, c1, c2]):
        raise ValueError("Invalid coordinates provided. All coordinates must be numbers.")

    # Ensure rectangle sides are horizontal and vertical (rephrased for clarity)
    if r1 != r2 and c1 != c2:
        raise ValueError("This algorithm requires the rectangle to have horizontal and vertical sides.")

    # Check for trivial cases (revised for conciseness and clarity)
    if (p1[0] < r1 and p2[0] < r1) or (p1[0] > r2 and p2[0] > r2) or (p1[1] < c2 and p2[1] < c2) or (
            p1[1] > c1 and p2[1] > c1):
        return False

    # Efficiently calculate the intersection point parameters
    denominator = (p2[0] - p1[0]) * (c2 - c1) - (p2[1] - p1[1]) * (r2 - r1)
    if denominator == 0:  # Check for parallel lines or coincident lines
        return False  # No intersection

    t = ((c1 - p1[1]) * (r2 - r1) - (c2 - p1[1]) * (r1 - p2[0])) / denominator
    u = ((p2[0] - p1[0]) * (c1 - p1[1]) - (p1[0] - r1) * (c2 - p1[1])) / denominator

    # Check if the intersection point is within the line segment (revised for efficiency and edge case handling)
    return 0 <= t <= 1 and 0 <= u <= 1


def random_string_generator():
    return ''.join(random.choice(string.ascii_lowercase) for i in range(10))


def main():
    global x1, y1, x2, y2
    while True:
        # Capture frame
        ret, frame = cap.read()

        # Convert to grayscale for efficiency
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)

        # for (x, y, w, h) in faces:
        #     cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        #     key = cv2.waitKey(1) & 0xFF
        #     # Capture image using cv2.imwrite()
        #     cv2.imwrite(f'images/{random_string_generator()}.jpg', frame)

        for (x, y, w, h) in faces:
            x_2 = x + w
            y_2 = y + h
            cv2.rectangle(frame, (x, y), (x + w, y + h), (252, 207, 32), 1)
            key = cv2.waitKey(1) & 0xFF
            if line_intersects_rectangle((x1, y1), (x2, y2), x, x_2, y, y_2):
                cv2.putText(frame, 'caught one', (x + 10, y + h - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            else:
                cv2.putText(frame, "can't find it", (x + 10, y + h - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # Display frame
        cv2.imshow('User Image', frame)

        # Exit on 'q' press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release resources
    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    login()
    setup_lock_configuration()
    main()
