import cv2
from picamera2 import Picamera2

piCam = Picamera2()
# Set the resolution of the camera
piCam.preview_configuration.main.size = (1280, 720)
piCam.preview_configuration.main.format = "RGB888"
piCam.preview_configuration.align()
piCam.configure("preview")
piCam.start()
while True:
    print("john")
    frame = piCam.capture_array()
    # Convert frame to BGR format
    print("john")
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    print("john")
    cv2.imshow("piCam", frame)
    print("john")
    # Wait indefinitely for key press to close window
    if cv2.waitKey(0) == ord('q'):
        break

cv2.destroyAllWindows()
