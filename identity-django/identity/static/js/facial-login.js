/**
 * 
 */
class UrlPaths {
    static get UPLOAD_FACIAL_DATA_URL() { return "/upload-facial-data/"; }
    static get PERFORM_SIGN_IN_URL() { return "/perform-sign-in/"; }
    static get PERFORM_SIGN_OUT_URL() { return "/perform-sign-out/"; }
}

/**
 * 
 */
class ResponseCodes {
    static get SUCCESS() { return 200; }
    static get ERROR() { return 500; }
    static get I_AM_A_TEAPOT() { return 418; }
}
/**
 * Using Unclaimed HTTP Response Codes starting at 460
 */
class MyResponseCodes {
    static get ALREADY_ON_ROASTER() { return 460; }
    static get LOCATION_PERMISSION_DENIED() { return 461; }
    static get NO_FACE_FOUND() { return 462; }
    static get NOT_ON_ROASTER() { return 463; }
}
const FACE_SAMPLE_COUNT = 30;

/**
 * 
 */
async function setupUserFacialRecognition() {

    let videoElement = document.getElementById('videoInput');


    let imageNumber = 1;
    const csrfToken = "";//document.querySelector('[name=csrfmiddlewaretoken]').value;
    const userAccountId = document.getElementById("user-account-id").value;
    while (imageNumber <= FACE_SAMPLE_COUNT) {

        var canvas = document.createElement("canvas");
        canvas.getContext('2d').drawImage(videoElement, 0, 0, canvas.width, canvas.height);
        let imageBase64Encoding = canvas.toDataURL();


        let options = buildUserFacialRecognitionSetUpOptions(imageBase64Encoding, imageNumber, userAccountId, csrfToken);
        let responseCode = await getResponseCode(UrlPaths.UPLOAD_FACIAL_DATA_URL, options);

        if (responseCode == ResponseCodes.NO_FACE_FOUND)
            continue;
        else if (responseCode == ResponseCodes.SUCCESS)
            imageNumber++;
        else
            break;
    }

    //messageUser("Face pictures taken");
}

/**
 * 
 * @param {*} imageBase64Encoding 
 * @param {*} imageNumber 
 * @param {*} userAccountId 
 * @param {*} csrfToken 
 * @returns 
 */
function buildUserFacialRecognitionSetUpOptions(imageBase64Encoding, imageNumber, userAccountId, csrfToken) {
    const formData = new FormData();
    const headers = {
        mode: 'same-origin',
        'X-CSRFToken': csrfToken,
    };

    formData.append('image-base64', imageBase64Encoding);
    formData.append('image-number', imageNumber);
    formData.append('user-account-id', userAccountId);

    const options = {
        body: formData,
        method: "POST",
        //headers: headers

    }
    return options;
}

/**
 * 
 */


async function streamSignInVideo() {
    let responseCode = await streamRoasterSigningVideo(UrlPaths.PERFORM_SIGN_IN_URL);
    let message = getMessage(responseCode);
    alert(message);
}

async function streamSignOutVideo() {
    let responseCode = await streamRoasterSigningVideo(UrlPaths.PERFORM_SIGN_OUT_URL);
    let message = getMessage(responseCode, false);
    alert(message);
}

/**
 * Streams the video from the webcam to the server to be processed for signing on/off the roaster
 * @param {String} url The url to send the request to
 * @returns A Response Code
 */
async function streamRoasterSigningVideo(url) {
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
        responseCode = await getResponseCode(url, options);
    }
    while (responseCode == MyResponseCodes.NO_FACE_FOUND)
    return responseCode;
}

/**
 * 
 * @param {Number} responseCode 
 * @param {boolean} signOn True if the user is signing on, false if the user is signing off
 * @returns 
 */
function getMessage(responseCode, signOn=true) {
    if (responseCode == ResponseCodes.SUCCESS) {
        if (signOn)
            return "Signed in completed";
        else
            return "Signed out completed";
    }
    else if (responseCode == MyResponseCodes.ALREADY_ON_ROASTER)
        return "You are already on the roaster";
    else if (responseCode == MyResponseCodes.LOCATION_PERMISSION_DENIED)
        return "You do not have permission to be at this location";
    else if (responseCode == MyResponseCodes.NOT_ON_ROASTER)
        return "You are not on the roaster";
    else if (responseCode >= 500) //500+ are server errors
        return `Server Error: Response Code:${responseCode}`;
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

/**
 * Gets the response code from the request to the given url with the given options. 
 * This function is asynchronous.
 * A response code of 418 means the request was not successful, but should be retried
 * A response code of 500 means the request was not successful, and should not be retried
 * A response code of 200 means the request was successful
 * @param {String} url The url to send the request to 
 * @param {Object} options The options for the request 
 * @returns 
 */
async function getResponseCode(url, options) {
    let responseCode;
    await fetch(url, options)
        .then(function (response) {
            responseCode = response.status;
        })
        .catch(function (err) {
            responseCode = ResponseCodes.ERROR;
        });
    return responseCode;
}

/**
 * @typedef {String} VideoResolutionFormatNames
 */
const VideoResolutionFormatNames = {
    QVGA: "qvga",
    VGA: "vga",
};

/**
 * @typedef {Object} VideoResolutionFormat
 */
const VideoResolutionFormats = {
    /**
     * @type {VideoResolutionFormat}
     */
    'qvga': { width: { exact: 320 }, height: { exact: 240 } },
    'vga': { width: { exact: 640 }, height: { exact: 480 } },
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