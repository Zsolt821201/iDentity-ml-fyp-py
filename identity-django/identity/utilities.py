import base64
import re
from io import BytesIO
from django.core.files.base import ContentFile
import cv2
from numpy import ndarray
from PIL import Image
from pathlib import Path


#CLASSIFIER_CONFIGURATION: str = str(Path(__file__).resolve().parent / 'haarcascades/haarcascade_frontalface_default.xml')
CLASSIFIER_CONFIGURATION: str = str(Path(__file__).resolve().parent / 'haarcascade_frontalface_default.xml')
DATABASE_DIRECTORY: str = str(Path(
    __file__).parent.parent / 'database/')
DATABASE_FACE_DIRECTORY: str = str(Path(
    __file__).parent.parent / 'database/identity_face_dataset')
DATABASE_FACIAL_TRAINER: str = str(Path(
    __file__).parent.parent / 'database/trainer.yml')

def decode_base64(data):
    image_data = re.sub('^data:image/.+;base64,', '', data)
    return base64.b64decode(image_data)

def stream_image(image) -> BytesIO:
    return BytesIO(decode_base64(image))

def base64_file(data, name=None):
    _format, _img_str = data.split(';base64,')
    _name, ext = _format.split('/')
    if not name:
        name = _name.split(":")[-1]
    return ContentFile(base64.b64decode(_img_str), name='{}.{}'.format(name, ext))

def get_user_face(user_account_id, image, image_number):
    gray_scale_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    face_detector_classifier = cv2.CascadeClassifier(CLASSIFIER_CONFIGURATION)
    faces: ndarray = face_detector_classifier.detectMultiScale(gray_scale_image, 1.3, 5)

    if len(faces) == 0:
        print("Error: No face detected")
        return False

    if len(faces) > 1:
        print("Error: More than one face detected")
        return False

    for (x, y, w, h) in faces:
        cv2.rectangle(image, (x, y), (x+w, y+h), (255, 0, 0), 2)
        image_path: str = f"{DATABASE_FACE_DIRECTORY}/user.{user_account_id}.{image_number}.jpg"
        cv2.imwrite(image_path, gray_scale_image[y:y+h, x:x+w])

        cv2.imshow('image', image)
    return True
