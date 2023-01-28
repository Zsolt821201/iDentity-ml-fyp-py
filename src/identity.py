# Copyright Zsolt Toth

from dataclasses import dataclass
import datetime
from numpy import ndarray
from pathlib import Path
import numpy
from PIL import Image
import cv2
import os
import sqlite3
from sqlite3 import Error

CLASSIFIER_CONFIGURATION: str = str(Path(
    __file__).parent / 'haarcascades/haarcascade_frontalface_default.xml')
DATABASE_DIRECTORY: str = str(Path(
    __file__).parent.parent / 'database/')
DATABASE_PATH: str = str(Path(
    __file__).parent.parent / 'database/identity.db')
DATABASE_FACE_DIRECTORY: str = str(Path(
    __file__).parent.parent / 'database/identity_face_dataset')
DATABASE_FACIAL_TRAINER: str = str(Path(
    __file__).parent.parent / 'database/trainer.yml')
FACE_SAMPLE_COUNT: int = 30
ESCAPE_KEY: int = 27


@dataclass
class UserAccount:
    id: int = 0
    email: str = ""
    enabled: bool = False
    face_recognition_enabled: bool = False
    first_name: str = ""
    is_twin: bool = False
    last_name: str = ""
    password: str = ""
    telephone: str = ""
    username: str = ""


class IdentifyService:
    connection: sqlite3.Connection = None

    def __init__(self, database_directory_path: str):
        self.database_directory_path = database_directory_path
        self.database_path: str = str(
            Path(database_directory_path) / 'identity.db')
        self.database_face_directory: str = str(
            Path(database_directory_path) / 'identity_face_dataset')
        self.database_facial_trainer: str = str(
            Path(database_directory_path) / 'trainer.yml')
        self.connection = sqlite3.connect(self.database_path)
        self.__user_account_service = UserAccountService(self)

    def get_user_account_service(self):
        return self.__user_account_service

    def get_last_inserted_row_id(self) -> int:
        cursor = self.connection.cursor()
        cursor.execute("SELECT last_insert_rowid()")
        return cursor.fetchone()[0]


class UserAccountService:

    def __init__(self, identify_service: IdentifyService):
        self.__user_account_repository = UserAccountRepository(
            identify_service)

    def get_user_accounts(self):
        return self.__user_account_repository.get_user_accounts()

    def get_user_account_by_id(self, user_account_id: str):
        return self.__user_account_repository.get_user_account_by_id(user_account_id)

    def save_user_account(self, user_account: UserAccount, images: list):
        user_account: self.__user_account_repository.save_user_account(
            user_account)
        if user_account.face_registration:
            save_images(user_account.id, images)
            regenerate_facial_trainer()
        return user_account


class UserAccountRepository:

    def __init__(self, identify_service: IdentifyService):
        self.__identify_service = identify_service

    def get_user_accounts(self):
        """
        Query all rows in the userAccount table
        Returns:
            list: list of users
        """
        cursor = self.__identify_service.connection.cursor()
        select_query = "SELECT * FROM UserAccount"
        cursor.execute(select_query)

        user_accounts = []
        rows = cursor.fetchall()

        print(rows)

        for row in rows:
            user_accounts.append(UserAccount(
                row[0], row[1], row[2] == 1, row[3] == 1, row[4], row[5] == 1, row[6], row[7], row[8], row[9]))

        return user_accounts

    def save_user_account(self, user_account: UserAccount):
        """
        Save user account
        Args:
            user_account (UserAccount): user account
        Returns:
            UserAccount: saved user account
        """
        cursor = self.__identify_service.connection.cursor()
        insert_query = "INSERT INTO UserAccount (email, enabled, face_recognition_enabled, first_name, is_twin, last_name, password, telephone, username) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
        cursor.execute(insert_query, (user_account.email, user_account.enabled, user_account.face_recognition_enabled, user_account.first_name,
                       user_account.is_twin, user_account.last_name, user_account.password, user_account.telephone, user_account.username))
        user_account.id = self.__identify_service.get_last_inserted_row_id()
        self.__identify_service.connection.commit()
        return user_account


def user_registration(user_account_id: str = "1"):
    """
    User face registration
    Args:
        user_account_id (str, optional): _description_. Defaults to "1".
    """
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
            image_path: str = f"{DATABASE_FACE_DIRECTORY}/user.{user_account_id}.{face_count}.jpg"
            cv2.imwrite(image_path, gray_scale_image[y:y+h, x:x+w])

            cv2.imshow('image', image)

        if cv2.waitKey(1) == ESCAPE_KEY:
            break
    # Do a bit of cleanup
    video_capture.release()
    cv2.destroyAllWindows()


def get_images_and_labels(path):

    image_paths = [os.path.join(path, f) for f in os.listdir(path)]
    face_samples = []
    ids = []

    detector = cv2.CascadeClassifier(CLASSIFIER_CONFIGURATION)

    for image_path in image_paths:

        PIL_img = Image.open(image_path).convert(
            'L')  # convert it to grayscale
        img_numpy = numpy.array(PIL_img, 'uint8')

        user_id = int(os.path.split(image_path)[-1].split(".")[1])
        faces = detector.detectMultiScale(img_numpy)

        for (x, y, w, h) in faces:
            face_samples.append(img_numpy[y:y+h, x:x+w])
            ids.append(user_id)

    return face_samples, ids


def face_training():
    print("\n [INFO] Training faces. It will take a few seconds. Wait ...")
    faces, ids = get_images_and_labels(DATABASE_FACE_DIRECTORY)

    recognizer = cv2.face.LBPHFaceRecognizer_create()

    recognizer.train(faces, numpy.array(ids))

    # Save the model into trainer/trainer.yml
    # recognizer.save() worked on Mac, but not on Pi
    recognizer.write(DATABASE_FACIAL_TRAINER)

    # Print the number of faces trained and end program
    print("\n [INFO] {0} faces trained. Exiting Program".format(
        len(numpy.unique(ids))))

# names related to ids: example ==> Marcelo: id=1,  etc
user_names = ['None', 'Zsolt', 'Paula', 'Ilza',
             'Z', 'W']  # TODO get from sql database
    
def face_recognition(user_names):
    """
    Face recognition
    

    Args:
        user_names (_type_): user names must be in the same order as in the database
        user_names must be unique
    """
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(DATABASE_FACIAL_TRAINER)

    faceCascade = cv2.CascadeClassifier(CLASSIFIER_CONFIGURATION)

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

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.2,
            minNeighbors=5,
            minSize=(int(minW), int(minH)),
        )

        for(x, y, w, h) in faces:

            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)

            id, confidence = recognizer.predict(gray[y:y+h, x:x+w])

            # Check if confidence is less them 100 ==> "0" is perfect match
            if (confidence < 100):
                id = user_names[id]
                confidence = "  {0}%".format(round(100 - confidence))
            else:
                id = "unknown"
                confidence = "  {0}%".format(round(100 - confidence))

            cv2.putText(img, str(id), (x+5, y-5), font, 1, (255, 255, 255), 2)
            cv2.putText(img, str(confidence), (x+5, y+h-5),
                        font, 1, (255, 255, 0), 1)

        cv2.imshow('camera', img)

        k = cv2.waitKey(10) & 0xff  # Press 'ESC' for exiting video
        if k == 27:
            break

    # Do a bit of cleanup
    print("\n [INFO] Exiting Program and cleanup stuff")
    cam.release()
    cv2.destroyAllWindows()


class Location:
    id: int = 0
    address: str = ""
    description: str = ""
    email: str = ""
    name: str = ""
    telephone: str = ""

    def __init__(self, id, address, description, email, name, telephone):
        self.id = 0
        self.address = ""
        self.description = ""
        self.email = ""
        self.name = ""
        self.telephone = ""


class LocationPermission:
    location_id: int = 0
    user_account_id: int = 0

    def __init__(self, location_id, user_account_id):
        self.location_id = location_id
        self.user_account_id = user_account_id


class Roster:
    id: int = 0
    location_id: int = 0
    sign_in_date_time: str = ""
    sign_out_date_time: str = ""
    user_account_id: int = 0

    def __init__(self, id, location_id, sign_in_date_time, sign_out_date_time, user_account_id):
        self.id = id
        self.location_id = location_id
        self.sign_in_date_time = sign_in_date_time
        self.sign_out_date_time = sign_out_date_time
        self.user_account_id = user_account_id


class Role:
    id: int = 0
    name: str = ""
    description: str = ""

    def __init__(self, id, name, description):
        self.id = id
        self.name = name
        self.description = description


class UserAccountRole:
    user_account_id: int = 0
    role_id: int = 0

    def __init__(self, user_account_id, role_id):
        self.user_account_id = user_account_id
        self.role_id = role_id


def main():
    user_registration()
    # face_training()
    # face_recognition()

def sql_test():
    admin_user_account = UserAccount(1, "admin@identify.com")
    admin_user_account.username = "admin"

    print(admin_user_account)
    print(admin_user_account.email)
    print(admin_user_account.username)

    identify_service = IdentifyService(DATABASE_DIRECTORY)

    user_accounts = identify_service.get_user_account_service().get_user_accounts()

    for user_account in user_accounts:
        print(user_account)

#    with connection:
 #       print ("1. Query select all user account:")
  #      select_all_users(connection)


if __name__ == "__main__":
    main()
