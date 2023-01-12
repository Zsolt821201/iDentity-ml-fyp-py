# Copyright Zsolt Toth

from numpy import ndarray
from pathlib import Path
import cv2
import os

CLASSIFIER_CONFIGURATION: str = str(Path(
    __file__).parent / 'haarcascades/haarcascade_frontalface_default.xml')
DATABASE_FACE_DIRECTORY: str = str(Path(
    __file__).parent.parent / 'database/identity_face_dataset')
FACE_SAMPLE_COUNT: int = 30
ESCAPE_KEY: int = 27


def user_registration(user_account_id: str = "1"):
    CAMERA_PORT: int = 0
    video_capture = cv2.VideoCapture(CAMERA_PORT)
    face_detector_classifier = cv2.CascadeClassifier(CLASSIFIER_CONFIGURATION)

    face_count: int = 0
    while(face_count < FACE_SAMPLE_COUNT):
        is_video_capture_open, image = video_capture.read()

        if not is_video_capture_open:
            print("Error: Camera is not opened")
            break

        cv2.imshow('image', image)

        gray_scale_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        faces: ndarray = face_detector_classifier.detectMultiScale(
            gray_scale_image, 1.3, 5)

        if len(faces) == 0:
            print("Error: No face detected")
            continue

        if len(faces) > 1:
            print("Error: More than one face detected")
            continue

        for (x, y, w, h) in faces:
            cv2.rectangle(image, (x, y), (x+w, y+h), (255, 0, 0), 2)
            face_count += 1
            image_path: str = f"{DATABASE_FACE_DIRECTORY}/user-{user_account_id}-{face_count}.jpg"
            cv2.imwrite(image_path, gray_scale_image[y:y+h, x:x+w])

            cv2.imshow('image', image)

        if cv2.waitKey(1) == ESCAPE_KEY:
            break
    # Do a bit of cleanup
    video_capture.release()
    cv2.destroyAllWindows()


def main():
    user_registration("1")


if __name__ == "__main__":
    main()
