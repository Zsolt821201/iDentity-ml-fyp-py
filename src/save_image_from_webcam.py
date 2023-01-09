# program to capture single image from webcam in python

# importing OpenCV library
import cv2
from cv2 import VideoCapture, imshow, imwrite, waitKey, destroyWindow

# initialize the camera
# If you have multiple camera connected with
# current device, assign a value in cam_port
# variable according to that
cameraPort:int = 0
cam:VideoCapture = cv2.VideoCapture(cameraPort)

# reading the input using the camera
success, image = cam.read()

# If image will detected without any error,
# show result
if success:

    # showing result, it take frame name and image
    # output
    windowName: str = "Web camera screen shot"
    imshow(windowName, image)

    # saving image in local storage
    filename: str = "web-camera-screen-shot.png"
    
    imwrite(filename, image)

    # Wait for keyboard interrupt
    waitKey(0)
    destroyWindow(windowName)

# If captured image is corrupted, moving to else part
else:
    print("No image detected. Please! try again")
