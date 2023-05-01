import cv2
from django.test import TestCase
import numpy
from PIL import Image
from .utilities import DATABASE_FACE_DIRECTORY, face_present_has_high_confidence
from .utilities import detect_user_face
from .utilities import get_images_and_labels
from .utilities import stream_image , face_recognition_web
from .utilities import build_sample_user

TEST_DATA_PATH:str = "identity/test-data/"
"""The path to the test data.  The 'test-data' directory cannot be named 'tests', because it will conflict with 'tests.py'
"""

class FaceRecognitionUtilityTests(TestCase):

    def test_get_images_and_labels(self):
        """
        get_images_and_labels must return 2 lists of the same length
        """
        faces, face_ids = get_images_and_labels(DATABASE_FACE_DIRECTORY)

        self.assertEqual(len(faces), len(face_ids))
        
    def test_detect_user_face(self):
        """
        detect_user_face must return a single face
        """
        image_path = f"{TEST_DATA_PATH}/image-with-one-face.jpg"
        open_cv_image = numpy.array(Image.open(image_path))
        gray_scale_image = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)
        
        is_face_present, face = detect_user_face(gray_scale_image)
        self.assertTrue(is_face_present)
        self.assertIsNotNone(face)
        
    def test_detect_face_with_blank(self):
        """
        detect_user_face must return a single face
        """
        image_path = f"{TEST_DATA_PATH}/no-face.jpg"
        open_cv_image = numpy.array(Image.open(image_path))
        
        gray_scale_image = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)
        
        is_face_present, face=detect_user_face(gray_scale_image)
        
        self.assertFalse(is_face_present)
        self.assertIsNone(face)

    def test_face_recognition_web(self):
        """
        detect_user_face must return a single face
        """
        image_path = f"{TEST_DATA_PATH}/secret/user-2.png"
        open_cv_image = numpy.array(Image.open(image_path))
        
        user_id, confidence = face_recognition_web(open_cv_image)
        
        expected_user_id = 2

        self.assertEquals(user_id,expected_user_id)
    
    def test_face_recognition_web_with_unknown_face(self):
        """
        detect_user_face must return a single face
        """
        image_path = f"{TEST_DATA_PATH}/arnold-schwarzenegger.jpg"
        open_cv_image = numpy.array(Image.open(image_path))
        
        user_id, confidence = face_recognition_web(open_cv_image)
        
        has_found_face: bool = user_id is not None and face_present_has_high_confidence(confidence)
        
        self.assertFalse(has_found_face)
        if has_found_face:
            self.assertIsNone(user_id)
    
    