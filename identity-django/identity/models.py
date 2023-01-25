from dataclasses import dataclass
import datetime
from numpy import ndarray
from pathlib import Path
import os
import sqlite3
from sqlite3 import Error

import cv2
import numpy
from PIL import Image
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class Location(models.Model):
    id = models.AutoField(primary_key=True)
    address = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    email = models.EmailField(max_length=200, unique=True)
    name = models.CharField(max_length=200, unique=True)
    telephone = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class LocationPermission(models.Model):
    location_id = models.ForeignKey(Location, on_delete=models.CASCADE)
    user_account_id = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )


class Roster(models.Model):
    id = models.AutoField(primary_key=True)
    location_id = models.ForeignKey(Location, on_delete=models.CASCADE)
    sign_in_date = models.DateTimeField('date signed in', auto_now_add=True)
    sign_out_date = models.DateTimeField(
        'date signed out', blank=True, null=True)
    user_account_id = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

class UserAccount(AbstractUser):
    is_face_recognition_enabled = models.BooleanField(default=False)
    is_twin = models.BooleanField(default=False)
    telephone = models.CharField(max_length=20, blank=True)
    
    def __str__(self):
        return self.get_username()
    
    # Add Update Method save user account  images to disk
   

CLASSIFIER_CONFIGURATION: str = str(Path(
    __file__).parent / 'haarcascades/haarcascade_frontalface_default.xml')
DATABASE_DIRECTORY: str = str(Path(
    __file__).parent.parent / 'database/')
DATABASE_FACE_DIRECTORY: str = str(Path(
    __file__).parent.parent / 'database/identity_face_dataset')
DATABASE_FACIAL_TRAINER: str = str(Path(
    __file__).parent.parent / 'database/trainer.yml')

   
def get_images_and_labels(path):

    image_paths = [os.path.join(path, f) for f in os.listdir(path)]
    face_samples = []
    ids = []

    detector = cv2.CascadeClassifier(CLASSIFIER_CONFIGURATION)

    for image_path in image_paths:

        image = Image.open(image_path).convert(
            'L')  # convert it to grayscale
        img_numpy = numpy.array(image, 'uint8')

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
    
    
