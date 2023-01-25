function createFileFromUrl (path, url, callback) {
    let request = new XMLHttpRequest();
    request.open('GET', url, true);
    request.responseType = 'arraybuffer';
    request.onload = function(ev) {
        if (request.readyState === 4) {
            if (request.status === 200) {
                let data = new Uint8Array(request.response);
                cv.FS_createDataFile('/', path, data, true, false, false);
                callback();
            } else {
                self.printError('Failed to load ' + url + ' status: ' + request.status);
            }
        }
    };
    request.send();
};
function startCamera(resolution, videoId) {
    const constraints = {
        'qvga': { width: { exact: 320 }, height: { exact: 240 } },
        'vga': { width: { exact: 640 }, height: { exact: 480 } }
    };
    let videoElement = document.getElementById(videoId);
    if (!videoElement) {
        videoElement = document.createElement('video');
    }

    let videoConstraint = constraints[resolution];
    if (!videoConstraint) {
        videoConstraint = true;
    }

    navigator.mediaDevices.getUserMedia({ video: videoConstraint, audio: false })
        .then(function (stream) {
            videoElement.srcObject = stream;
            videoElement.play();
        })
        .catch(function (err) {
            console.error('Camera Error: ' + err.name + ' ' + err.message);
        });
}
function setUpFacialRecognition() {
    const FACE_SAMPLE_COUNT = 30;
    const CLASSIFIER_CONFIGURATION = "https://raw.githubusercontent.com/kipr/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml";//"haarcascade_frontalface_default.xml";
    let videoInputElement = document.getElementById('videoInput');


    let videoCapture = new cv.VideoCapture(videoInputElement);
    let faceDetectorClassifier = new cv.CascadeClassifier();
    faceDetectorClassifier.load(CLASSIFIER_CONFIGURATION);


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
        // schedule the next one.
        let delay = 1000 / FPS - (Date.now() - begin);
        setTimeout(processVideo, delay);
    };

    // schedule the first one.
    setTimeout(processVideo, 0);
}