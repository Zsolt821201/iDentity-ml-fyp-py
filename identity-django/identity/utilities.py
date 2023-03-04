import base64
from datetime import datetime
import os
import re
from io import BytesIO
from cv2 import CascadeClassifier
from django.core.files.base import ContentFile
import cv2
from numpy import ndarray
from PIL import Image
from pathlib import Path

import numpy

from .models import Location, LocationPermission, Roster, UserAccount


#CLASSIFIER_CONFIGURATION: str = str(Path(__file__).resolve().parent / 'haarcascades/haarcascade_frontalface_default.xml')

PARENT_DIRECTORY: Path = Path(__file__).resolve().parent.parent
CLASSIFIER_CONFIGURATION: str = str(
    PARENT_DIRECTORY / 'haarcascade_frontalface_default.xml')
DATABASE_DIRECTORY: str = str(PARENT_DIRECTORY / 'database/')
DATABASE_FACE_DIRECTORY: str = str(
    PARENT_DIRECTORY / 'database/identity_face_dataset')
DATABASE_LOG_DIRECTORY: str = str(
    PARENT_DIRECTORY / 'database/log')
DATABASE_FACIAL_TRAINER: str = str(PARENT_DIRECTORY / 'database/trainer.yml')
FACE_CONFIDENCE_LEVEL:float = 80.0


class MyResponseCodes :
    """_summary_
    Using Unclaimed HTTP Response Codes starting at 460
    @see https://developer.mozilla.org/en-US/docs/Web/HTTP/Status#client_error_responses
    @see Last paragraph of https://www.rfc-editor.org/rfc/rfc2616#section-6.1.1
    """
    ALREADY_ON_ROASTER: int = 460
    LOCATION_PERMISSION_DENIED: int = 461
    NO_FACE_FOUND: int = 462
    NOT_ON_ROASTER: int = 463

def base64_file(data, name=None):
    _format, _img_str = data.split(';base64,')
    _name, ext = _format.split('/')
    if not name:
        name = _name.split(":")[-1]
    return ContentFile(base64.b64decode(_img_str), name='{}.{}'.format(name, ext))

def build_sample_user(video_path:str, session_user_account_id:str):
    
    video_capture = cv2.VideoCapture(video_path)
    face_detector_classifier = cv2.CascadeClassifier(CLASSIFIER_CONFIGURATION)

    image_number: int = 0
    FACE_SAMPLE_COUNT=30
    ESCAPE_KEY: int = 27
    while(image_number < FACE_SAMPLE_COUNT):
        is_video_capture_open, open_cv_image = video_capture.read()

        if not is_video_capture_open:
            print("Error: Camera is not opened")
            break

        cv2.imshow('image', open_cv_image)

        gray_scale_image = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)

        faces: ndarray = face_detector_classifier.detectMultiScale(
            gray_scale_image, 1.3, 5)

        face_found = detect_and_save_user_face(
            session_user_account_id, open_cv_image, image_number)
        if face_found:
            image_number += 1

        

        for (x, y, w, h) in faces:
            cv2.rectangle(open_cv_image, (x, y), (x+w, y+h), (255, 0, 0), 2)
            cv2.imshow('image', open_cv_image)

        if cv2.waitKey(1) == ESCAPE_KEY:
            break
    # Do a bit of cleanup
    video_capture.release()
    cv2.destroyAllWindows()

def decode_base64(image_base64_str):
    image_data = re.sub('^data:image/.+;base64,', '', image_base64_str)
    return base64.b64decode(image_data)


def detect_and_save_user_face(user_account_id, image, image_number):
    """Detects a single face in the image and saves it to the database"""
    gray_scale_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    face_found, face = detect_user_face(gray_scale_image)
    if face_found:
        x, y, w, h = face
        directory: str = f"{DATABASE_FACE_DIRECTORY}/user-{user_account_id}"
        os.makedirs(directory, exist_ok=True)
        cv2.imwrite(f"{directory}/{image_number}.jpg",
                    gray_scale_image[y:y+h, x:x+w])

    return face_found

def detect_user_face(gray_scale_image, min_size=None) -> tuple[bool,ndarray]:
    """
    Detects a single face in the image and returns the face coordinates
    The face_detector_classifier detects any faces found in a image.  It returns a flag found as True with the face is detected.
    If no face is detected, the flag found is False.  If more than one face is detected, the flag found is False.

    Args:
        gray_scale_image (_type_): _description_
        min_size (tuple, optional): _description_. Defaults to None.

    Returns:
        tuple[bool,ndarray]: _description_
    """

    face_detector_classifier = cv2.CascadeClassifier(CLASSIFIER_CONFIGURATION)
    faces: ndarray = face_detector_classifier.detectMultiScale(
        gray_scale_image, scaleFactor=1.3, minNeighbors=5, minSize=min_size)

    if len(faces) == 0:
        print("Error: No face detected")
        return False, None

    if len(faces) > 1:
        print("Error: More than one face detected")
        return False, None


    return True, faces[0]


def stream_image(image_base64_str: str) -> BytesIO:
    return BytesIO(decode_base64(image_base64_str))

def face_image_recognition(recognizer: cv2.face.LBPHFaceRecognizer, img, min_size = None):
    gray_scale_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    is_face_present, face = detect_user_face(gray_scale_image, min_size=min_size)
    
    if(not is_face_present):
        return None, 0, None
    
    x, y, width, height = face
    user_id, confidence = recognizer.predict(gray_scale_image[y:y+height, x:x+width])
    
    # log_attempt(user_id, confidence, face)
    
    return user_id, confidence, face

def log_attempt(user_id, confidence, face):
    """Not Working

    Args:
        user_id (_type_): _description_
        confidence (_type_): _description_
        face (_type_): _description_
    """
    file_path: str = f"{DATABASE_LOG_DIRECTORY}/{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}user-{user_id}-confidence-{confidence}.jpg"
    os.makedirs(file_path, exist_ok=True)
    cv2.imwrite(f"{file_path}", face)
    
def face_recognition_web(open_cv_image: ndarray):
    """
    Face recognition


    Args:
        user_names (_type_): user names must be in the same order as in the database
        user_names must be unique
    """
    
    recognizer:cv2.face.LBPHFaceRecognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(DATABASE_FACIAL_TRAINER)

    user_id, confidence, face = face_image_recognition(recognizer,  open_cv_image)

    return user_id, confidence

def face_training():
    print("\n [INFO] Training faces. It will take a few seconds. Wait ...")
    faces, face_ids = get_images_and_labels(DATABASE_FACE_DIRECTORY)

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.train(faces, numpy.array(face_ids))

    os.makedirs(DATABASE_DIRECTORY, exist_ok=True)
    # Save the model into trainer/trainer.yml
    recognizer.write(DATABASE_FACIAL_TRAINER)
    # recognizer.save() worked on Mac, but not on Pi

    # Print the number of faces trained and end program
    print("\n [INFO] {0} faces trained. Exiting Program".format(
        len(numpy.unique(face_ids))))

def get_images_and_labels(path) -> tuple[list, list]:
    """ Get the faces and labels from the training images.
    The directory structure is as follows:
    database/identity_face_dataset/user-1/1.jpg

    Each image is named as the user id and the image number.  Each image is a face image of the user.

    Args:
        path (str): _description_
        list (_type_): _description_

    Returns:
        _type_: _description_
    """
    face_ids: list[str] = []
    face_samples: list[ndarray] = []

    user_directories = [os.path.join(path, directory)
                        for directory in os.listdir(path)]
    for user_directory in user_directories:
        user_image_files = [os.path.join(
            user_directory, file) for file in os.listdir(user_directory)]
        face_id = int(os.path.split(user_directory)[-1].split("-")[1])

        for image_path in user_image_files:
            face_image_numpy: ndarray = numpy.array(
                Image.open(image_path), 'uint8')
            face_samples.append(face_image_numpy)
            face_ids.append(face_id)

    return face_samples, face_ids


def face_present_has_high_confidence(loss: float) -> bool:
    """ Determines if the face is present and identified by the loss value.
        

    Args:
        loss (float): _description_

    Returns:
        bool: Returns true, indicating the system believes a an identified face is present If the loss is less than the FACE_CONFIDENCE_LEVEL.
        Otherwise, returns false indicating the system believes an unidentified face is present.
        
    """
    return loss <= FACE_CONFIDENCE_LEVEL
    

def is_permission_denied(user_account : UserAccount, location: Location) -> bool:
    location_permission: LocationPermission = LocationPermission.objects.filter(
        location=location, user_account=user_account).first()

    return location_permission is None


def is_on_active_roster(user_account, location: Location) -> bool:
    """_summary_

    Args:
        user_account (_type_): _description_
        location (Location): _description_

    Returns:
        bool: _description_
    """
    roster: Roster = Roster.objects.filter(
        location=location, user_account=user_account, sign_out_date__isnull=True).first()
    return roster is not None

def parse_roaster_signing_requests(request) -> tuple[bool, UserAccount]:
    request_data = request.POST

    image_bytes = stream_image(request_data['image-base64'])

    open_cv_image = numpy.array(Image.open(image_bytes))

    user_id, confidence = face_recognition_web(open_cv_image)

    face_found = user_id is not None and face_present_has_high_confidence(confidence)
    
    print(f"User id: {user_id}, confidence {confidence}, face_found: {face_found}")

    return face_found, user_id

def sign_in_at_location(user_account: UserAccount, location: Location):
    sign_in_date = datetime.now()
    roster: Roster = Roster(location=location,
                            user_account=user_account,
                            sign_in_date=sign_in_date)
    roster.save()


def sign_out_at_location(user_account: UserAccount, location: Location):
    roster: Roster = Roster.objects.filter(
        location=location, user_account=user_account, sign_out_date__isnull=True).first()
    roster.sign_out_date = datetime.now()
    roster.save()










    