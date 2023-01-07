import numpy as np

import cv2

cascPath = "src/open_cv_test/haarcascade_frontalface_default.xml"
eyeCascPath = "src/open_cv_test/haarcascade_eye.xml"


face_cascade = cv2.CascadeClassifier(cascPath)

eye_cascade = cv2.CascadeClassifier(eyeCascPath)

cap = cv2.VideoCapture(0)

while True:

    _, img = cap.read()

    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray, 1.5, 5)

    for (x,y,width,height) in faces:

        cv2.rectangle(img,(x,y),(x+width,y+height),(255,0,0),2)

        roi_gray = gray[y:y+height, x:x+width]

        roi_color = img[y:y+height, x:x+width]

        eyes = eye_cascade.detectMultiScale(roi_gray)

        for (ex,ey,ew,eh) in eyes:

            cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)

    print(f"found {len(faces)} face(s)")

    cv2.imshow('img',img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    

cap.release()

cv2.destroyAllWindows()