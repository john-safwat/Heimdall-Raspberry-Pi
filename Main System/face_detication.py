import cv2
from picamera2 import Picamera2
import random
import string


def random_string_generator():
    return ''.join(random.choice(string.ascii_lowercase) for i in range(10))


piCam = Picamera2()
# set the resolution of the camera
piCam.preview_configuration.main.size = (640, 360)
piCam.preview_configuration.main.format = "RGB888"  # we use RGB888 because opencv uses BGR
piCam.preview_configuration.align()
piCam.configure("preview")
piCam.start()

# Initialize camera
cap = cv2.VideoCapture(0)  # Change number for different camera indices

# Load pre-trained face detector
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

for i in range(20):
    frame = piCam.capture_array()
    # Convert to grayscale for efficiency
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Detect faces
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (35, 20, 32), 1)
        key = cv2.waitKey(1) & 0xFF
        # Capture image using cv2.imwrite()
        cv2.imwrite(f'images/{random_string_generator()}.jpg', frame)

    # Display frame
    cv2.imshow('User Image', frame)

    # Exit on 'q' press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
