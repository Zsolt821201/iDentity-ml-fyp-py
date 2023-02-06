

function createFileFromUrl(url, filename) {
    let request = new XMLHttpRequest();
    request.open('GET', url, true);
    request.responseType = 'arraybuffer';
    request.onload = function (_) {
        if (request.readyState === 4) {
            if (request.status === 200) {
                let data = new Uint8Array(request.response);
                let thing = cv.FS_createDataFile('/', filename, data, true, false, false);
                console.log(thing)
            } else {
                console.error('Failed to load ' + url + ' status: ' + request.status);
            }
        }
    };
    request.send();
};

function setUpFacialRecognition() {
    let begin = Date.now();

    let faceCascadeFile = "haarcascade_frontalface_default.xml"
    let faceCascadeFileUrl = "https://raw.githubusercontent.com/kipr/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml"
    //let faceCascadeFileUrl  ="http://127.0.0.1:8000/static/haarcascade_frontalface_default.xml"

    createFileFromUrl(faceCascadeFileUrl, faceCascadeFile);

    const CLASSIFIER_CONFIGURATION = "https://raw.githubusercontent.com/kipr/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml";//"haarcascade_frontalface_default.xml";
    let videoInputElement = document.getElementById('videoInput');


    let videoCapture = new cv.VideoCapture(videoInputElement);
    let faceDetectorClassifier = new cv.CascadeClassifier();
    faceDetectorClassifier.load(faceCascadeFile);


    let src = new cv.Mat(videoInputElement.height, videoInputElement.width, cv.CV_8UC4);

    let canvasOutputElement = document.getElementById('canvasOutput');
    let dst = new cv.Mat(canvasOutputElement.height, canvasOutputElement.width, cv.CV_8UC4);


    const FPS = 30;

    let faceImages = [];
    let face_count = 0;

    while (face_count < FACE_SAMPLE_COUNT) {
        videoCapture.read(src);
        src.copyTo(dst);

        let gray_scale_image = new cv.Mat();
        cv.cvtColor(dst, gray_scale_image, cv.COLOR_RGBA2GRAY, 0);

        try {
            let faces = new cv.RectVector();
            faceDetectorClassifier.detectMultiScale(gray_scale_image, faces, 1.1, 3, 0);

            if (faces.size() == 0) {
                console.log("Error: No face detected");
            }

            if (faces.size() > 1) {
                console.log("Error: More than one face detected");
            }

            // draw faces.
            for (const face of faces) {
                let point1 = new cv.Point(face.x, face.y);
                let point2 = new cv.Point(face.x + face.width, face.y + face.height);
                cv.rectangle(dst, point1, point2, [255, 0, 0, 255]);
                face_count += 1
                faceImages.push(dst);
            }
            cv.imshow('canvasOutput', dst);
        }
        catch (err) {
            console.log(err);
        }
        // schedule the next one.
        let delay = 1000 / FPS - (Date.now() - begin);
        setTimeout(setUpFacialRecognition, delay);
    };
}
