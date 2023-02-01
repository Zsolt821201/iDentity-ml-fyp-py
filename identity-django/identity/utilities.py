import base64
import os
import re
from io import BytesIO
from django.core.files.base import ContentFile
import cv2
from numpy import ndarray
from PIL import Image
from pathlib import Path

import numpy


#CLASSIFIER_CONFIGURATION: str = str(Path(__file__).resolve().parent / 'haarcascades/haarcascade_frontalface_default.xml')

PARENT_DIRECTORY: Path = Path(__file__).resolve().parent.parent
CLASSIFIER_CONFIGURATION: str = str(PARENT_DIRECTORY / 'haarcascade_frontalface_default.xml')
DATABASE_DIRECTORY: str = str(PARENT_DIRECTORY / 'database/')
DATABASE_FACE_DIRECTORY: str = str(PARENT_DIRECTORY / 'database/identity_face_dataset')
DATABASE_FACIAL_TRAINER: str = str(PARENT_DIRECTORY / 'database/trainer.yml')

def decode_base64(image_base64_str):
    image_data = re.sub('^data:image/.+;base64,', '', image_base64_str)
    return base64.b64decode(image_data)


def stream_image(image_base64_str: str) -> BytesIO:
    return BytesIO(decode_base64(image_base64_str))


def base64_file(data, name=None):
    _format, _img_str = data.split(';base64,')
    _name, ext = _format.split('/')
    if not name:
        name = _name.split(":")[-1]
    return ContentFile(base64.b64decode(_img_str), name='{}.{}'.format(name, ext))


def detect_user_face(gray_scale_image):
    face_detector_classifier = cv2.CascadeClassifier(CLASSIFIER_CONFIGURATION)
    faces: ndarray = face_detector_classifier.detectMultiScale(
        gray_scale_image, 1.3, 5)

    if len(faces) == 0:
        print("Error: No face detected")
        return False, faces

    if len(faces) > 1:
        print("Error: More than one face detected")
        return False, faces

    return True, faces[0]


def detect_and_save_user_face(user_account_id, image, image_number):
    gray_scale_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    face_found, face = detect_user_face(gray_scale_image)
    if face_found:
        x, y, w, h = face
        directory: str = f"{DATABASE_FACE_DIRECTORY}/user-{user_account_id}"
        os.makedirs(directory, exist_ok=True)
        cv2.imwrite(f"{directory}/{image_number}.jpg",
                    gray_scale_image[y:y+h, x:x+w])

    return face_found


def get_images_and_labels(path):
    face_ids = []
    face_samples = []

    user_directories = [os.path.join(path, directory)
                        for directory in os.listdir(path)]
    for user_directory in user_directories:
        user_image_files = [os.path.join(
            user_directory, file) for file in os.listdir(user_directory)]
        face_id = int(os.path.split(user_directory)[-1].split("-")[1])

        for image_path in user_image_files:
            face_image_numpy = numpy.array(Image.open(image_path), 'uint8')
            face_samples.append(face_image_numpy)
            face_ids.append(face_id)

    return face_samples, face_ids


def face_training():
    print("\n [INFO] Training faces. It will take a few seconds. Wait ...")
    faces, face_ids = get_images_and_labels(DATABASE_FACE_DIRECTORY)

    recognizer = cv2.face.LBPHFaceRecognizer_create()

    recognizer.train(faces, numpy.array(face_ids))

    # Save the model into trainer/trainer.yml
    # recognizer.save() worked on Mac, but not on Pi
    os.makedirs(DATABASE_DIRECTORY, exist_ok=True)
    recognizer.write(DATABASE_FACIAL_TRAINER)

    # Print the number of faces trained and end program
    print("\n [INFO] {0} faces trained. Exiting Program".format(
        len(numpy.unique(face_ids))))

def face_recognition(user_names):
    """
    Face recognition
    

    Args:
        user_names (_type_): user names must be in the same order as in the database
        user_names must be unique
    """
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(DATABASE_FACIAL_TRAINER)

    face_cascade = cv2.CascadeClassifier(CLASSIFIER_CONFIGURATION)

    font = cv2.FONT_HERSHEY_SIMPLEX

    # iniciate id counter
    id = 0


    cam = cv2.VideoCapture(0)

    # Define min window size to be recognized as a face
    minW = 0.1*cam.get(3)
    minH = 0.1*cam.get(4)

    while True:

        _, img = cam.read()
        # img = cv2.flip(img, -1) # Flip vertically

        user_id, confidence = face_image_recognition(user_names, recognizer, face_cascade, font, minW, minH, img)

            # Check if confidence is less them 100 ==> "0" is perfect match
        if (confidence < 100):
            user_id = user_names[user_id]
            confidence = "  {0}%".format(round(100 - confidence))
        else:
            user_id = "unknown"
            confidence = "  {0}%".format(round(100 - confidence))

        #cv2.putText(img, str(user_id), (x+5, y-5), font, 1, (255, 255, 255), 2)
        #cv2.putText(img, str(confidence), (x+5, y+h-5),font, 1, (255, 255, 0), 1)
        cv2.imshow('camera', img)

        k = cv2.waitKey(10) & 0xff  # Press 'ESC' for exiting video
        if k == 27:
            break

    # Do a bit of cleanup
    print("\n [INFO] Exiting Program and cleanup stuff")
    cam.release()
    cv2.destroyAllWindows()


def face_recognition_web(user_names, img):
    """
    Face recognition
    

    Args:
        user_names (_type_): user names must be in the same order as in the database
        user_names must be unique
    """
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(DATABASE_FACIAL_TRAINER)

    face_cascade = cv2.CascadeClassifier(CLASSIFIER_CONFIGURATION)

    font = cv2.FONT_HERSHEY_SIMPLEX



    user_id, confidence = face_image_recognition(user_names, recognizer, face_cascade, font, minW, minH, img)

        # Check if confidence is less them 100 ==> "0" is perfect match
    if (confidence < 100):
        user_id = user_names[user_id]
        confidence = "  {0}%".format(round(100 - confidence))
    else:
        user_id = "unknown"
        confidence = "  {0}%".format(round(100 - confidence))

    #cv2.putText(img, str(user_id), (x+5, y-5), font, 1, (255, 255, 255), 2)
    #cv2.putText(img, str(confidence), (x+5, y+h-5),font, 1, (255, 255, 0), 1)
    cv2.imshow('camera', img)



def face_image_recognition(user_names, recognizer, face_cascade, font, minW, minH, img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.2,
            minNeighbors=5,
            minSize=(int(minW), int(minH)),
        )
    
    if len(faces) == 0:
        print("Error: No face detected")
        return False, faces

    if len(faces) > 1:
        print("Error: More than one face detected")
        return False, faces

    for(x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)

        user_id, confidence = recognizer.predict(gray[y:y+h, x:x+w])
        print(f"Confidence of {user_names[user_id]}: {confidence}");

        if (confidence >= 100):
            user_id = -1
        return user_id, confidence
    
    return -1, -1
