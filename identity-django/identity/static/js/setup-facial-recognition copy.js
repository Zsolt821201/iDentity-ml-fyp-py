// TODO: JavaScript 
// Save 30 images to a request

function saveImages(images)
{
  const userAccountId = document.getElementById("user-account-id").value;
  const formData = new FormData();

  formData.append('user-account-id', userAccountId);
  images.forEach(image => {
    formData.append('images', image);
  });

  const options = {
    body: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    method: "POST",
  }


  fetch("/upload-facial-data", options)
  .then(response => response.json())
  .then(data => {
    console.log(data);
  });

}

// Post the request to the server

// If the server returns a success, clear the images from the canvas, alert user

//This function, clearCanvasOnSuccess, takes in a response object as an argument. 
//It checks if the status property of the response is equal to "success". 
//If it is, it calls the clearCanvas function which has the code to clear the images from the canvas. 
//It also alerts the user that the images have been cleared from the canvas.
//You can call the function by passing the response from server like this : clearCanvasOnSuccess(serverResponse);
function clearCanvasOnSuccess(response) {
    if (response.status === "success") {
        clearCanvas();
        alert("Success! Images have been cleared from the canvas.");
    }
}
// Clear the canvas of all images
// This function, clearCanvas, is used to clear the images from the canvas. It first gets the canvas element by its id using document.getElementById("myCanvas") and gets the 2D rendering context using canvas.getContext("2d").
// Then it uses the clearRect method on the context object to clear the entire canvas. The clearRect method takes four arguments: the x-coordinate and y-coordinate of the top-left corner of the rectangle to be cleared, and the width and height of the rectangle. In this case, the entire canvas is being cleared (0, 0, canvas.width, canvas.height) which starts from top left corner to bottom right corner.

// Note: Make sure to replace "myCanvas" with the actual id of your canvas element in the HTML.

// You can call this function when ever you want to clear the canvas, after calling this function all the images on the canvas will be removed.
function clearCanvas() {
    var canvas = document.getElementById("myCanvas");
    var context = canvas.getContext("2d");
    context.clearRect(0, 0, canvas.width, canvas.height);
}



    function Utils(errorOutputId) { // eslint-disable-line no-unused-vars
        let self = this;
        this.errorOutput = document.getElementById(errorOutputId);
    
        const OPENCV_URL = "https://docs.opencv.org/4.x/opencv.js" //'https://cdn.jsdelivr.net/npm/opencv.js@1.2.1/opencv.js';
        this.loadOpenCv = function(onloadCallback) {
            let script = document.createElement('script');
            script.setAttribute('async', '');
            script.setAttribute('type', 'text/javascript');
            script.addEventListener('load', async () => {
                if (cv.getBuildInformation)
                {
                    console.log(cv.getBuildInformation());
                    onloadCallback();
                }
                else
                {
                    // WASM
                    if (cv instanceof Promise) {
                        cv = await cv;
                        console.log(cv.getBuildInformation());
                        onloadCallback();
                    } else {
                        cv['onRuntimeInitialized']=()=>{
                            console.log(cv.getBuildInformation());
                            onloadCallback();
                        }
                    }
                }
            });
            script.addEventListener('error', () => {
                self.printError('Failed to load ' + OPENCV_URL);
            });
            script.src = OPENCV_URL;
            let node = document.getElementsByTagName('script')[0];
            node.parentNode.insertBefore(script, node);
        };
    
        this.createFileFromUrl = function(path, url, callback) {
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
    
        this.loadImageToCanvas = function(url, cavansId) {
            let canvas = document.getElementById(cavansId);
            let ctx = canvas.getContext('2d');
            let img = new Image();
            img.crossOrigin = 'anonymous';
            img.onload = function() {
                canvas.width = img.width;
                canvas.height = img.height;
                ctx.drawImage(img, 0, 0, img.width, img.height);
            };
            img.src = url;
        };
    
        this.executeCode = function(textAreaId) {
            try {
                this.clearError();
                let code = document.getElementById(textAreaId).value;
                eval(code);
            } catch (err) {
                this.printError(err);
            }
        };
    
        this.clearError = function() {
            this.errorOutput.innerHTML = '';
        };
    
        this.printError = function(err) {
            if (typeof err === 'undefined') {
                err = '';
            } else if (typeof err === 'number') {
                if (!isNaN(err)) {
                    if (typeof cv !== 'undefined') {
                        err = 'Exception: ' + cv.exceptionFromPtr(err).msg;
                    }
                }
            } else if (typeof err === 'string') {
                let ptr = Number(err.split(' ')[0]);
                if (!isNaN(ptr)) {
                    if (typeof cv !== 'undefined') {
                        err = 'Exception: ' + cv.exceptionFromPtr(ptr).msg;
                    }
                }
            } else if (err instanceof Error) {
                err = err.stack.replace(/\n/g, '<br>');
            }
            this.errorOutput.innerHTML = err;
        };
    
        this.loadCode = function(scriptId, textAreaId) {
            let scriptNode = document.getElementById(scriptId);
            let textArea = document.getElementById(textAreaId);
            if (scriptNode.type !== 'text/code-snippet') {
                throw Error('Unknown code snippet type');
            }
            textArea.value = scriptNode.text.replace(/^\n/, '');
        };
    
        this.addFileInputHandler = function(fileInputId, canvasId) {
            let inputElement = document.getElementById(fileInputId);
            inputElement.addEventListener('change', (e) => {
                let files = e.target.files;
                if (files.length > 0) {
                    let imgUrl = URL.createObjectURL(files[0]);
                    self.loadImageToCanvas(imgUrl, canvasId);
                }
            }, false);
        };
    
        function onVideoCanPlay() {
            if (self.onCameraStartedCallback) {
                self.onCameraStartedCallback(self.stream, self.video);
            }
        };
    
        this.startCamera = function(resolution, callback, videoId) {
            const constraints = {
                'qvga': {width: {exact: 320}, height: {exact: 240}},
                'vga': {width: {exact: 640}, height: {exact: 480}}};
            let video = document.getElementById(videoId);
            if (!video) {
                video = document.createElement('video');
            }
    
            let videoConstraint = constraints[resolution];
            if (!videoConstraint) {
                videoConstraint = true;
            }
    
            navigator.mediaDevices.getUserMedia({video: videoConstraint, audio: false})
                .then(function(stream) {
                    video.srcObject = stream;
                    video.play();
                    self.video = video;
                    self.stream = stream;
                    self.onCameraStartedCallback = callback;
                    video.addEventListener('canplay', onVideoCanPlay, false);
                })
                .catch(function(err) {
                    self.printError('Camera Error: ' + err.name + ' ' + err.message);
                });
        };
    
        this.stopCamera = function() {
            if (this.video) {
                this.video.pause();
                this.video.srcObject = null;
                this.video.removeEventListener('canplay', onVideoCanPlay);
            }
            if (this.stream) {
                this.stream.getVideoTracks()[0].stop();
            }
        };
    };
    let utils = new Utils('errorMessage');

    utils.loadCode('codeSnippet', 'codeEditor');
    
    let streaming = false;
    let videoInput = document.getElementById('videoInput');
    let startAndStop = document.getElementById('startAndStop');
    let canvasOutput = document.getElementById('canvasOutput');
    let canvasContext = canvasOutput.getContext('2d');
    
    startAndStop.addEventListener('click', () => {
        if (!streaming) {
            utils.clearError();
            utils.startCamera('qvga', onVideoStarted, 'videoInput');
        } else {
            utils.stopCamera();
            onVideoStopped();
        }
    });
    
    function onVideoStarted() {
        streaming = true;
        startAndStop.innerText = 'Stop';
        videoInput.width = videoInput.videoWidth;
        videoInput.height = videoInput.videoHeight;
        utils.executeCode('codeEditor');
    }
    
    function onVideoStopped() {
        streaming = false;
        canvasContext.clearRect(0, 0, canvasOutput.width, canvasOutput.height);
        startAndStop.innerText = 'Start';
    }
    
    utils.loadOpenCv(() => {
        let faceCascadeFile = "./haarcascade_frontalface_default.xml"
        let faceCascadeFileUrl  = "https://raw.githubusercontent.com/kipr/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml"
        //let faceCascadeFileUrl  ="http://127.0.0.1:8000/static/haarcascade_frontalface_default.xml"
        utils.createFileFromUrl(faceCascadeFile, faceCascadeFileUrl, () => {
            startAndStop.removeAttribute('disabled');
        });
    });
    

    const FACE_SAMPLE_COUNT = 30;

    
    let video = document.getElementById('videoInput');
    let src = new cv.Mat(canvasOutputElement.height, canvasOutputElement.width, cv.CV_8UC4);
    let dst = new cv.Mat(canvasOutputElement.height, canvasOutputElement.width, cv.CV_8UC4);
    let gray = new cv.Mat();
    let cap = new cv.VideoCapture(canvasOutputElement);
    let faces = new cv.RectVector();
    let classifier = new cv.CascadeClassifier();
    
    // load pre-trained classifiers
    faceDetectorClassifier.load("haarcascade_frontalface_default.xml");
    
    var faceImages =[];

    const FPS = 30;
    function processVideo() {
        try {
            if (!streaming) {
                // clean and stop.
                src.delete();
                dst.delete();
                gray.delete();
                faces.delete();
                faceDetectorClassifier.delete();
                return;
            }
            let begin = Date.now();
            // start processing.
            videoCapture.read(src);
            src.copyTo(dst);
            cv.cvtColor(dst, gray, cv.COLOR_RGBA2GRAY, 0);
            // detect faces.
            faceDetectorClassifier.detectMultiScale(gray, faces, 1.1, 3, 0);

            console.log("# Faces found: "+faces.size());
            if(faces.size() == 0)
            {
                console.log("Error: No face detected");
            }
    
            if(faces.size() > 1)
            {
                console.log("Error: More than one face detected");
            }

            // draw faces.
            for (let i = 0; i < faces.size(); ++i) {
                let face = faces.get(i);
                let point1 = new cv.Point(face.x, face.y);
                let point2 = new cv.Point(face.x + face.width, face.y + face.height);
                cv.rectangle(dst, point1, point2, [255, 0, 0, 255]);
                while(faceImages.Length < FACE_SAMPLE_COUNT)
                {
                    faceImages.push(dst);
                }
            }
            cv.imshow('canvasOutput', dst);
            // schedule the next one.
            let delay = 1000/FPS - (Date.now() - begin);
            setTimeout(processVideo, delay);
        } catch (err) {
            utils.printError(err);
        }
    };
    
    // schedule the first one.
    setTimeout(processVideo, 0);