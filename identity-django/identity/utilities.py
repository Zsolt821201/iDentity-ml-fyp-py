from .models import Location, LocationPermission, Roster, UserAccount
from datetime import datetime
from cv2 import CascadeClassifier
from django.core.files.base import ContentFile
from io import BytesIO
from numpy import ndarray
from pathlib import Path
from PIL import Image

import base64
import cv2
import numpy
import os
import re



#CLASSIFIER_CONFIGURATION: str = str(Path(__file__).resolve().parent / 'haarcascades/haarcascade_frontalface_default.xml')

# Define the parent directory of the current file
PARENT_DIRECTORY: Path = Path(__file__).resolve().parent.parent
# Path to the classifier configuration file (haarcascade_frontalface_default.xml)
CLASSIFIER_CONFIGURATION: str = str(
    PARENT_DIRECTORY / 'haarcascade_frontalface_default.xml')
# Path to the database directory
DATABASE_DIRECTORY: str = str(PARENT_DIRECTORY / 'database/')
# Path to the face directory within the database directory
DATABASE_FACE_DIRECTORY: str = str(
    PARENT_DIRECTORY / 'database/identity_face_dataset')
# Path to the log directory within the database directory
DATABASE_LOG_DIRECTORY: str = str(
    PARENT_DIRECTORY / 'database/log')
# Path to the facial trainer file within the database directory
DATABASE_FACIAL_TRAINER: str = str(PARENT_DIRECTORY / 'database/trainer.yml')
# Face recognition confidence level threshold
FACE_CONFIDENCE_LEVEL:float = 85.0


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

###
# File IO
###
def base64_file(data, name=None):
    """
    Convert a base64 encoded data string into a Django ContentFile object.

    :param data: A base64 encoded data string including the format.
    :param name: Optional custom name for the file.
    :return: A Django ContentFile object containing the decoded data.
    """ 
    _format, _img_str = data.split(';base64,')
    _name, ext = _format.split('/')
    if not name:
        name = _name.split(":")[-1]
    return ContentFile(base64.b64decode(_img_str), name='{}.{}'.format(name, ext))

def decode_base64(image_base64_str):
    """
    Decode a base64 encoded image string.

    :param image_base64_str: A base64 encoded image string including the format.
    :return: A bytes object containing the decoded image data.
    """
    image_data = re.sub('^data:image/.+;base64,', '', image_base64_str)
    return base64.b64decode(image_data)

def stream_image(image_base64_str: str) -> BytesIO:
    """
    Convert a base64 encoded image string into a BytesIO stream.

    :param image_base64_str: A base64 encoded image string including the format.
    :return: A BytesIO object containing the decoded image data.
    """
    return BytesIO(decode_base64(image_base64_str))


def build_sample_user(video_path:str, session_user_account_id:str):
    """
    Capture face samples from a video source and save them for a user account.

    :param video_path: The file path or device index of the video source.
    :param session_user_account_id: The ID of the user account for which face samples are being collected.
    """
    # Initializing video capture object and face detector classifier    
    video_capture = cv2.VideoCapture(video_path)
    face_detector_classifier = cv2.CascadeClassifier(CLASSIFIER_CONFIGURATION)

    image_number: int = 0
    FACE_SAMPLE_COUNT=30
    ESCAPE_KEY: int = 27
     # Capture face samples until the desired sample count is reached or the user presses the escape key
    while(image_number < FACE_SAMPLE_COUNT):
        is_video_capture_open, open_cv_image = video_capture.read()

        if not is_video_capture_open: # Camera is not opened
            break

        cv2.imshow('image', open_cv_image)
         # Convert the image to grayscale for face detection
        gray_scale_image = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)
        # Detect faces in the image
        faces: ndarray = face_detector_classifier.detectMultiScale(
            gray_scale_image, 1.3, 5)
        # Detect and save user face and increment image_number if a face is found
        face_found = detect_and_save_user_face(
            session_user_account_id, open_cv_image, image_number)
        if face_found:
            image_number += 1

        
        # Draw rectangles around detected faces and display the image
        for (x, y, w, h) in faces:
            cv2.rectangle(open_cv_image, (x, y), (x+w, y+h), (255, 0, 0), 2)
            cv2.imshow('image', open_cv_image)
        # Exit the loop if the escape key is pressed
        if cv2.waitKey(1) == ESCAPE_KEY:
            break
    # Do a bit of cleanup
    video_capture.release()
    cv2.destroyAllWindows()



# Step 1 detect faces
def detect_and_save_user_face(user_account_id, image, image_number):
    """
    Detects a single face in the image and saves it to the specified directory.

    :param user_account_id: The ID of the user account for which the face is being detected.
    :param image: The image in which to detect the face.
    :param image_number: The index number for the image to be saved.
    :return: A boolean indicating if a face was found.
    """
    # Convert the image to grayscale for face detection
    gray_scale_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Detect user face in the grayscale image
    face_found, face = detect_user_face(gray_scale_image)
    if face_found:
        # If a face is found, extract the coordinates and dimensions
        x, y, w, h = face
        # Create the directory for the user's face images if it doesn't exist
        directory: str = f"{DATABASE_FACE_DIRECTORY}/user-{user_account_id}"
        os.makedirs(directory, exist_ok=True)
        # Save the detected face region as a grayscale image
        cv2.imwrite(f"{directory}/{image_number}.jpg",
                    gray_scale_image[y:y+h, x:x+w])

    return face_found

def detect_user_face(gray_scale_image, min_size=None) -> tuple[bool,ndarray]:
    """
    Detects a single face in the image and returns the face coordinates
    The face_detector_classifier detects any faces found in a image.  It returns a flag found as True with the face is detected.
    If no face is detected, the flag found is False.  If more than one face is detected, the flag found is False.

    Args:
        gray_scale_image (Mat): Take a gray-scale image Mat object as input
        min_size (tuple, optional): _description_. Defaults to None.

    Returns:
        tuple[bool,ndarray]: _description_
    """

    face_detector_classifier = cv2.CascadeClassifier(CLASSIFIER_CONFIGURATION)
    faces: ndarray = face_detector_classifier.detectMultiScale(
        gray_scale_image, scaleFactor=1.3, minNeighbors=5, minSize=min_size)

    if len(faces) == 0: # No face detected
        return False, None

    if len(faces) > 1: # More than one face detected
        print("More than one face detected")
        return False, None


    return True, faces[0]

# Step 3 recognize faces
def face_image_recognition(recognizer: cv2.face.LBPHFaceRecognizer, image, min_size = None):
    """
    Recognize a face in an image using the LBPH face recognizer.

    :param recognizer: A trained cv2.face.LBPHFaceRecognizer object.
    :param image: The image in which to recognize the face.
    :param min_size: Optional minimum size of the face to be detected.
    :return: A tuple containing the user ID, confidence, and face coordinates (x, y, width, height).
    """
    # Convert the image to grayscale for face recognition
    gray_scale_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Detect a user face in the grayscale image
    is_face_present, face = detect_user_face(gray_scale_image, min_size=min_size)
    # If a face is not present, return None for user ID, 0 for confidence, and None for face coordinates
    if(not is_face_present):
        return None, 0, None
    # Extract the coordinates and dimensions of the face
    x, y, width, height = face
    # Predict the user ID and confidence using the recognizer
    user_id, confidence = recognizer.predict(gray_scale_image[y:y+height, x:x+width])
    
    # log_attempt(user_id, confidence, face)
    
    return user_id, confidence, face

    
def face_recognition_web(open_cv_image: ndarray):
    """
    Perform face recognition on a given image using a pre-trained LBPH face recognizer.

    :param open_cv_image: An OpenCV image (numpy ndarray) in which to recognize the face.
    :return: A tuple containing the user ID and confidence of the recognized face.
    """
    # Create an LBPH face recognizer and load the pre-trained model from the database
    recognizer:cv2.face.LBPHFaceRecognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(DATABASE_FACIAL_TRAINER)
    # Call the face_image_recognition function to recognize the face and obtain user ID and confidence
    user_id, confidence, _ = face_image_recognition(recognizer,  open_cv_image)

    return user_id, confidence

# Step 2 train faces
def face_training():
    """
    Train an LBPH face recognizer using the face images stored in the database directory and save the model.
    """
    print("\n [INFO] Training faces. It will take a few seconds. Wait ...")
    # Get face images and their corresponding labels from the database directory
    faces, face_ids = get_images_and_labels(DATABASE_FACE_DIRECTORY)
    # Create an LBPH face recognizer and train it using the collected face images and labels
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
    """
    Get the faces and labels from the training images.

    The directory structure is as follows:
    database/identity_face_dataset/user-1/1.jpg

    Each image is named as the user id and the image number.
    Each image is a face image of the user.

    Args:
        path (str): The path to the directory containing the user images.

    Returns:
        tuple: A tuple containing two lists - a list of face images (numpy arrays), and a list of face IDs (integers).
    """
    face_ids: list[str] = []
    face_samples: list[ndarray] = []
    # Get the user directories
    user_directories = [os.path.join(path, directory)
                        for directory in os.listdir(path)]
    for user_directory in user_directories:
        # Get the image files for each user
        user_image_files = [os.path.join(
            user_directory, file) for file in os.listdir(user_directory)]
        face_id = int(os.path.split(user_directory)[-1].split("-")[1])

        for image_path in user_image_files:
            # Read the face image as a numpy array
            face_image_numpy: ndarray = numpy.array(
                Image.open(image_path), 'uint8')
            # Add the face image and face ID to the respective lists
            face_samples.append(face_image_numpy)
            face_ids.append(face_id)

    return face_samples, face_ids



###
### Support for IDentity Model API
###

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
    """
    Check if a user is denied permission to access a specified location.

    :param user_account: A UserAccount object representing the user to check.
    :param location: A Location object representing the location to check.
    :return: A boolean indicating if the user's permission is denied.
    """
    # Find the LocationPermission object that matches the user account and location
    location_permission: LocationPermission = LocationPermission.objects.filter(
        location=location, user_account=user_account).first()
    # Return True if the location permission is not found, otherwise return False
    return location_permission is None


def is_on_active_roster(user_account, location: Location) -> bool:
    """_summary_This is_on_active_roste function that takes a user account and a location as argument
        and checks if the user is currently on the active roster for that location. 
        The function returns a boolean value indicating whether or not the user is on the active roster.

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
    """
    Process an incoming request containing an image in base64 format and perform face recognition.

    :param request: An HttpRequest object containing the POST data with a base64-encoded image.
    :return: A tuple containing a boolean indicating if a face was found, and the corresponding UserAccount.
    """
    request_data = request.POST # Extract the request data from the POST request
    # Convert the base64 image to bytes
    image_bytes = stream_image(request_data['image-base64'])
    # Create a numpy array from the image bytes
    open_cv_image = numpy.array(Image.open(image_bytes))
    # Perform face recognition on the image
    user_id, confidence = face_recognition_web(open_cv_image)
    # Check if a face was found and if the recognition confidence is high
    face_found = user_id is not None and face_present_has_high_confidence(confidence)
    
    print(f"User id: {user_id}, confidence {confidence}, face_found: {face_found}")

    return face_found, user_id

def sign_in_at_location(user_account: UserAccount, location: Location):
    """
    Sign in a user at a specified location and save the sign-in record to the Roster model.

    :param user_account: A UserAccount object representing the user who is signing in.
    :param location: A Location object representing the sign-in location.
    """
    sign_in_date = datetime.now()# Get the current date and time
    # Create a new Roster object with the user account, location, and sign-in date
    roster: Roster = Roster(location=location,
                            user_account=user_account,
                            sign_in_date=sign_in_date)
    roster.save() # Save the new Roster object to the database

def sign_out_at_location(user_account: UserAccount, location: Location):
    """
    Sign out a user at a specified location and update the sign-out record in the Roster model.

    :param user_account: A UserAccount object representing the user who is signing out.
    :param location: A Location object representing the sign-out location.
    """
    # Find the Roster object that matches the user account and location, and has a null sign-out date
    roster: Roster = Roster.objects.filter(
        location=location, user_account=user_account, sign_out_date__isnull=True).first()
    # Set the sign-out date to the current date and time
    roster.sign_out_date = datetime.now()
    # Save the updated Roster object to the database
    roster.save()

###
### Logging
###

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
    
###
### Build Sample User Accounts
###

def build_user_josha_fluke():
    image_path = "identity/tests/dummy-data/josha-fluke.mp4"
    build_sample_user(image_path, "3")
    
    
