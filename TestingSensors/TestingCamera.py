import cv2
from picamera2 import  Picamera2
piCam = Picamera2()
#set the resolution of the camera
piCam.preview_configuration.main.size=(1280,720)
piCam.preview_configuration.main.format="RGB888" #we use RGB888 because opencv uses BGR
piCam.preview_configuration.align()
piCam.configure("preview")
piCam.start()
while True:
    frame = piCam.capture_array()
    cv2.imshow("piCam",frame)
    if cv2.waitKey(1) == ord('q'):
        break
cv2.destroyAllWindows()