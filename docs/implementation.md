
# Implementation

# Frameworks/Lanaguages

Python
Javascript

Django
OpenCV

## Using Django

To use Django, you need to install Python and Django. 

## Create a new Django project

Create a new Django project: Once Django is installed, you can create a new project by running the following command:

```bash
django-admin startproject identity_website
```

Replace project_name with the name of your project. This command will create a new directory with the same name as your project, which will contain the basic files and folders needed to start a new Django project.

Create a new Django app: A Django project is made up of one or more apps. An app is a module that contains models, views, templates, and other code that serves a specific purpose. You can create a new app by running the following command:

```bash
python manage.py startapp identity
```

Replace app_name with the name of your app. This command will create a new directory with the same name as your app, which will contain the basic files and folders needed to start a new Django app.

## The Models

Django will implement the database using the definitions in the `models.py` file.  The developer never has to write SQL code.  The `models.py` file is where you define the data structures for your application.  Each class in `models.py` represents a table in the database.  Each attribute of the class represents a column in the table.  The following code defines a Location class that represents a table in the database.

eg.

  ```python
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
  ```
  
  creates a Table in the database
  
  ```sql
  CREATE TABLE "identity_location" 
  ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
   "address" varchar(200) NOT NULL,
    "description" varchar(200) NOT NULL, "email" varchar(200) NOT NULL UNIQUE, "name" varchar(200) NOT NULL UNIQUE, "telephone" varchar(20) NOT NULL)
  ```

To create the database perform the migrations.

### Migrations

Note `0001` increments with each migration.

```bash
python manage.py makemigrations identity
python manage.py sqlmigrate identity 0001
python manage.py migrate
```

```bash
python manage.py migrate
```

### Overriding the default User Model

## The Views

`views.py` is where you define the logic for your application. It is where you define the functions used when a user visits a particular URL. Each function in views.py acts as a controller in a traditional MVC application.

user sercurity is handled by the `@login_required` decorator. placed on functions in the `views.py` file.

```python

```python
View used the templaes

### The Templates

Html files are stored in a project folder called `templates`. The templates folder must be located in the same directory as the `views.py` file.

For example, the following code defines a function called `index` that returns a rendered template `website/index.html` relative to the templates folder.

```python
def index(request):
    return render(request, 'website/index.html')
```

### The Static Files

### Passing Data to Templates (The Context)

The context is a dictionary that contains the data that is passed to the template.  The context is passed to the render function as the third parameter.

The named parameters in the context are then available in the template as variables.  For example, the following code defines a function called `setup_facial_recognition` that returns a rendered template from `user-accounts/setup-facial-recognition.html` relative to the templates folder.

views.py

```python
def setup_facial_recognition(request):
    user_account = get_object_or_404(UserAccount, pk=request.user.id)
    context = { 'user_account_id': user_account.id }
    return render(request, 'user-accounts/setup-facial-recognition.html', context)
```

user-accounts/setup-facial-recognition.html

```django
{% extends "master.html" %}
{% load static %}
{% block content %}
    <div class="column">
        <h2>User Facial Recognition Setup</h2>
        <p>Please look directly at the camera until your face is detected and profile recorded.</p>
        <video id="videoInput" width="320" height="240">
        </video>
        <p id="errorMessage" class="error"></p>
        <input type="hidden"
               id="user-account-id"
               name="user-account-id"
               value="{{ user_account_id }}"/>
        <button id="startButton"
                class="btn btn-primary"
                onClick="setupUserFacialRecognition()">
            Setup User Facial Recognition
        </button>
        <p id="statusMessage"></p>
    </div>
{% endblock content %}
{% block scripts %}
    <script src="{% static "js/facial-login.js" %}"></script>
    <script type="text/javascript">startCamera(VideoResolutionFormatNames.QVGA, 'videoInput');</script>
{% endblock scripts %}
```

### Extending templates

A base template is a template that other templates extend. Generally they contain the HTML that is common to all pages in your application with named blocks that other templates can override with view specific content. This allows you to avoid duplicating the same HTML in multiple templates.  For example, a base template might contain the HTML for the header, footer, and navigation bar. Then other templates can then extend the base template and add their own HTML content for the named blocks.

For example, the following code blocks defines a base template called master.html with a title block and login.html extends the base template and overrides the title block.

master.html

```django
<html lang="en">
    <head>
        <title>Identity
            {% block title %}
            {% endblock title %}
        </title>
    </head>
    <body></body>
</html>
```

login.html

```django
{% extends 'identity/master.html' %}
{% block title %}Login{% endblock title %}
```

Only the content between the block tags is needed to create view. The rest of the HTML is inherited from the base template.

## The Admin


## The Urls

Maps the URL to the functions defined in views.py.

## The Forms

## Using Open CV /Utilities

I placed the Application Code for Image Processing in utilities.py

haarcascades are pre-trained classifiers that are used to detect objects in images.
The identity project used `haarcascade_frontalface_default.xml` to detect faces in images.

## Constants and File Paths

Constants for FilePaths and application Settings are defined at the top of the `utilities.py` file.

```python
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
```

`FACE_CONFIDENCE_LEVEL` is the maximum confidence level acceptable that a face can be considered a match.  The lower the value the more confident the application is that the face is a identified correctly. File paths are defined relative to the `utilities.py` file for teh directories that are used by the application, such as the `database` directory, the `database/identity_face_dataset` directory, and the `database/trainer.yml` file.

### Open CV

### How to use Open CV

The opencv-python package is a Python wrapper for the OpenCV library.  This package must be installed to use opencv in the application. c.f. 6.4 To install and Run the project.

Import the package using the following code in python files.

```python
import cv2
```

#### How to find a face in an image

Given a gray-scale image Mat object as input the function `detect_user_face` returns a tuple containing a boolean flag and a numpy array.  The flag is True if a face is detected in the image and False if no face is detected.  The numpy array contains the coordinates of the face in the image.

[detect_user_face](https://github.com/Zsolt821201/iDentity-ml-fyp-py/blob/25b7eaa48465b378fb8faf3ed1d705b32a05e284/identity-django/identity/utilities.py)

```python
def detect_user_face(gray_scale_image, min_size=None) -> tuple[bool,ndarray]:
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
```

`face_detector_classifier = cv2.CascadeClassifier(CLASSIFIER_CONFIGURATION)` loads the classifier configuration file into the face_detector_classifier object.  The `detectMultiScale` method of the face_detector_classifier object is used to detect faces in the image.  The `detectMultiScale` method returns a numpy array of faces. The `detect_user_face` function checks for the cases of (1) no face detected and (2) more than one face detected.  If either of these cases occur, the function returns False and None.  If a single face is detected, the function returns True and the coordinates of the face in the image.

detect_and_save_user_face

```python
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
```

The `detect_and_save_user_face` function takes a user account id, an image, and an image number as input.  The function converts the image to a gray-scale image and calls the `detect_user_face` function to detect a face in the image.  If a face is detected, the function saves the face to the database directory.  The function returns a boolean flag indicating whether a face was detected.

#### How to train the model

The `face_training` function trains the model using the images in the `DATABASE_FACE_DIRECTORY` directory.  The function saves the trained model to the `DATABASE_FACIAL_TRAINER` file. `recognizer = cv2.face.LBPHFaceRecognizer_create()` creates a face recognizer object.  The `recognizer.train` method takes the list of images and the list of user ids as input and trains the model. With the model trained `recognizer.write` method saves the trained model to the `DATABASE_FACIAL_TRAINER` file.

```python
def face_training():
    faces, face_ids = get_images_and_labels(DATABASE_FACE_DIRECTORY)

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.train(faces, numpy.array(face_ids))

    # Ensure the database directory exists before saving the model
    os.makedirs(DATABASE_DIRECTORY, exist_ok=True)
    # Save the model into trainer/trainer.yml
    recognizer.write(DATABASE_FACIAL_TRAINER)
```

The function `get_images_and_labels` returns a tuple of lists (1) a list of images of the users faces from the directory `DATABASE_FACE_DIRECTORY` and (2) a list of user ids.  The structure of the directory is users ids as subdirectories that contain 30 images of the users face

```python
def get_images_and_labels(path) -> tuple[list, list]:
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
```

#### How to recognize a face in an image


### File Encoding


### Creating Sample users

For demonstration purposes, sample users were created using Youtube videos.  The following code creates a sample user taking a video from Youtube.

```python
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
```

## Unit Testing

### How to run the unit tests
