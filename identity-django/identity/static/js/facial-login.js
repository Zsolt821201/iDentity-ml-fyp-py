/**
 * 
 */
class UrlPaths {
    static get UPLOAD_FACIAL_DATA_URL() { return "/upload-facial-data/"; }
    static get PERFORM_SIGN_IN_URL() { return "/perform-sign-in/"; }
}


async function streamSignInVideo() {
    //TODO: Implement facial login

    let videoElement = document.getElementById('videoInput');
    let imageNumber = 0;
    const locationId = document.getElementById("location-id").value;

    const csrfToken = "";//document.querySelector('[name=csrfmiddlewaretoken]').value;
    let responseCode;
    do {

        var canvas = document.createElement("canvas");
        canvas.getContext('2d').drawImage(videoElement, 0, 0, canvas.width, canvas.height);
        let imageBase64Encoding = canvas.toDataURL();


        //wait one second before taking the next picture
        const fiveSeconds = 5000;
        await new Promise(handler => setTimeout(handler, fiveSeconds));
        let options = buildSignInOptions(imageBase64Encoding, imageNumber, locationId, csrfToken);
        responseCode = await getResponseCode(UrlPaths.PERFORM_SIGN_IN_URL, options);
    }
    while (responseCode == 418)

    if (responseCode == 200)
        alert("signed in completed");
    //redirectUserToDashboard();
    else // responseCode == ERROR/500
        console.log("Error: " + responseCode);
}

/**
 * 
 * @param {String} imageBase64Encoding  The base64 encoding of the image to upload
 * @param {Number} imageNumber The number of the image being uploaded
 * @param {Number} locationId The id of the location the user is signing in at
 * @param {String} csrfToken The CSRF token for the request
 * @returns 
 */
function buildSignInOptions(imageBase64Encoding, imageNumber, locationId, csrfToken) {
    const formData = new FormData();
    const headers = {
        mode: 'same-origin',
        'X-CSRFToken': csrfToken,
    };

    formData.append('image-base64', imageBase64Encoding);
    formData.append('image-number', imageNumber);
    formData.append('location-id', locationId);

    const options = {
        body: formData,
        method: "POST",
        //headers: headers
    }
    return options;
}
async function getResponseCode(url, options) {
    let responseCode = await executeRequest(url, options);
    return responseCode;
}


async function executeRequest(url, options) {
    let responseCode = 418;//I'm a teapot
    await fetch(url, options)
        .then(function (response) { responseCode = response.status; })
        .catch(function (err) {
            responseCode = 500;//Internal Server Error
        });
    return responseCode;
}

/**
 * @typedef {String} VideoResolutionFormatNames
 */
const VideoResolutionFormatNames = {
    QVGA: "qvga",
    VGA:  "vga",
};

/**
 * @typedef {Object} VideoResolutionFormat
 */
const VideoResolutionFormats = {
    /**
     * @type {VideoResolutionFormat}
     */
    'qvga': { width: { exact: 320 }, height: { exact: 240 } },
    'vga':  { width: { exact: 640 }, height: { exact: 480 } },
};

/**
 * Starts the camera and displays the video stream without audio on the video element.  If the video element does not exist, it will be created.
 * @param {VideoResolutionFormatNames} resolution 
 * @param {String} videoId The HTML element id of the video element to display the video stream on.
 */
function startCamera(resolution, videoId) {

    let videoElement = document.getElementById(videoId);
    if (!videoElement) {
        videoElement = document.createElement('video');
    }

    let videoConstraint = VideoResolutionFormats[resolution];
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