import cv2
from picamera2 import  Picamera2
import random
import string


def random_string_generator():
    return ''.join(random.choice(string.ascii_letters + string.punctuation) for x in range(5))


piCam = Picamera2()
#set the resolution of the camera
piCam.preview_configuration.main.size=(1280,720)
piCam.preview_configuration.main.format="RGB888" #we use RGB888 because opencv uses BGR
piCam.preview_configuration.align()
piCam.configure("preview")
piCam.start()

# Initialize camera
cap = cv2.VideoCapture(0)  # Change number for different camera indices

# Load pre-trained face detector
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

while True:
    frame = piCam.capture_array()


    # Convert to grayscale for efficiency
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        # Display consent message and capture upon pressing 'c'
        consent_message = "Press 'c' to capture image with consent (or any other key to continue)"
        cv2.putText(frame, consent_message, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        key = cv2.waitKey(1) & 0xFF
        
        # Capture image using cv2.imwrite()
        cv2.imwrite(f'images/{random_string_generator()}.jpg', frame)
        # Display capture completion message or visual cue
        cv2.putText(frame, "Image captured!", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.waitKey(1000)  # Display message for 1 second

    # Draw rectangles around detected faces (if any)
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

    # Display frame
    cv2.imshow('frame', frame)

    # Exit on 'q' press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
