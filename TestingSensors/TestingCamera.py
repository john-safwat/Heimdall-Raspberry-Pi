import cv2
from picamera2 import Picamera2

piCam = Picamera2()
# set the resolution of the camera
piCam.preview_configuration.main.size = (1280, 720)
piCam.preview_configuration.main.format = "RGB888"  # we use RGB888 because opencv uses BGR
piCam.preview_configuration.align()
piCam.configure("preview")
piCam.start()
# set up camera object
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)
# QR code detection object
detector = cv2.QRCodeDetector()

while True:
    _, img = cap.read()
    # detect and decode
    data, bbox, _ = detector.detectAndDecode(img)
    # check if there is a QRCode in the image
    if data:
        print(data)
    # Below will display the live camera feed to the Desktop on Raspberry Pi OS preview
    cv2.imshow("code detector", img)
    if cv2.waitKey(1) == ord('q'):
        break
cv2.destroyAllWindows()
