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
    y1 = int(y1_coordinate.val())
    y2_coordinate = pyrebase_database.child(f"Locks/{lock_id}/y2_value").get(token)
    y2 = int(y2_coordinate.val())
    x1_coordinate = pyrebase_database.child(f"Locks/{lock_id}/x1_value").get(token)
    x1 = int(x1_coordinate.val())
    x2_coordinate = pyrebase_database.child(f"Locks/{lock_id}/x2_value").get(token)
    x2 = int(x2_coordinate.val())


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


def is_line_and_rectangle_intersected(x, y, w, h, line1_p1, line1_p2):
    if are_lines_intersected(line1_p1, line1_p2, (x, y), (x + w, y)):
        return True
    elif are_lines_intersected(line1_p1, line1_p2, (x, y), (x, y + h)):
        return True
    elif are_lines_intersected(line1_p1, line1_p2, (x, y + h), (x + w, y + h)):
        return True
    elif are_lines_intersected(line1_p1, line1_p2, (x + w, y + h), (x + w, y)):
        return True
    else:
        return False


def are_lines_intersected(line1_p1, line1_p2, line2_p1, line2_p2):
    """
    This function checks if two lines defined by their end points intersect.

    Args:
        line1_p1: A tuple (x, y) representing the first point of line 1.
        line1_p2: A tuple (x, y) representing the second point of line 1.
        line2_p1: A tuple (x, y) representing the first point of line 2.
        line2_p2: A tuple (x, y) representing the second point of line 2.

    Returns:
        True if the lines intersect, False otherwise.
    """

    # Calculate the direction vectors of the lines
    line1_dir = (line1_p2[0] - line1_p1[0], line1_p2[1] - line1_p1[1])
    line2_dir = (line2_p2[0] - line2_p1[0], line2_p2[1] - line2_p1[1])

    # Check if the lines are parallel
    if line1_dir[0] * line2_dir[1] == line1_dir[1] * line2_dir[0]:
        return False  # Lines are parallel and don't intersect

    # Calculate the determinant to check for intersection
    denominator = line1_dir[0] * line2_dir[1] - line1_dir[1] * line2_dir[0]

    # Lines are collinear if the denominator is close to zero
    if abs(denominator) < 1e-6:
        return False  # Lines are collinear and may or may not intersect

    # Calculate the intersection point (if it exists)
    t1 = ((line2_p2[0] - line2_p1[0]) * (line1_p1[1] - line2_p1[1]) -
          (line2_p2[1] - line2_p1[1]) * (line1_p1[0] - line2_p1[0])) / denominator
    t2 = ((line1_p2[0] - line1_p1[0]) * (line1_p1[1] - line2_p1[1]) -
          (line1_p2[1] - line1_p1[1]) * (line1_p1[0] - line2_p1[0])) / denominator

    # Check if the intersection point lies on the line segments
    if 0 <= t1 <= 1 and 0 <= t2 <= 1:
        return True  # Lines intersect

    return False  # Lines don't intersect


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
            cv2.rectangle(frame, (x, y), (x + w, y + h), (252, 207, 32), 1)
            key = cv2.waitKey(1) & 0xFF

            print(is_line_and_rectangle_intersected(x, y, w, h, (x1, y1), (x2, y2)))

            if is_line_and_rectangle_intersected(x, y, w, h, (x1, y1), (x2, y2)):
                cv2.putText(frame, 'caught one', (x + 10, y + h - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            else:
                cv2.putText(frame, "can't find it", (x + 10, y + h - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 1)

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
