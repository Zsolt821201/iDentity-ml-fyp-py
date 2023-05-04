"use strict";
/**
 * A class representing custom response codes for various server responses.
 * Using Unclaimed HTTP Response Codes starting at 460
 */
class MyResponseCodes {
	static get ALREADY_ON_ROASTER() { return 460; }
	static get LOCATION_PERMISSION_DENIED() { return 461; }
	static get NO_FACE_FOUND() { return 462; }
	static get NOT_ON_ROASTER() { return 463; }
}

/**
 * A class representing standard HTTP response codes.
 * Response code for a successful HTTP request. 200 OK
 * response code for an internal server error. 500 Internal Server Error
 * response code for a server that is refusing to brew coffee because it is, permanently, a teapot. 418 I'm a teapot
 */
class ResponseCodes {
	static get SUCCESS() { return 200; }
	static get ERROR() { return 500; }
	static get I_AM_A_TEAPOT() { return 418; }
}

/**
 * A class representing the URL paths for various facial recognition api.
 * 
 */
class UrlPaths {
	static get IDENTIFY_USER_FROM_FACE_URL() { return "/identify-user-from-face/"; }
	static get PERFORM_SIGN_IN_URL() { return "/perform-sign-in/"; }
	static get PERFORM_SIGN_OUT_URL() { return "/perform-sign-out/"; }
	static get UPLOAD_FACIAL_DATA_URL() { return "/upload-facial-data/"; }
}

/**
 * An object containing video resolution format names as constants
 * @typedef {String} VideoResolutionFormatNames
 */
const VideoResolutionFormatNames = {
	QVGA: "qvga", // Quarter Video Graphics Array resolution
	VGA: "vga", // Video Graphics Array resolution
};

/**
 * An object containing video resolution formats with their exact width and height values.
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
 * WebPageControls
 * WebPageControls class encapsulates the DOM elements used in the facial recognition web page
 * @class
 * @classdesc Accesses the required elements of the web page
 */
class WebPageControls {
	/**
	 * Creates a new instance of WebPageControls
	 * @constructor
	 * @param {String} videoElementId 
	 */
	constructor(
		abortButtonId = "abortButton",
		accessControlId = "accessControl",
		autoSignInCountDownId = "auto-sign-in-count-down",
		detectedUserPanelId = "detectedUserPanel",
		locationFieldId = "location-id",
		statusMessageId = "statusMessage",
		startButtonId = "startButton",
		stopButtonId = "stopButton",
		usernameId = "username",
		videoId = "videoInput") {
		this.abortButton = document.getElementById(abortButtonId);
		this.accessControlElement = document.getElementById(accessControlId);
		this.autoSignInCountDownElement = document.getElementById(autoSignInCountDownId);
		this.detectedUserPanel = document.getElementById(detectedUserPanelId);
		this.locationField = document.getElementById(locationFieldId);
		this.startButton = document.getElementById(startButtonId);
		this.statusMessageElement = document.getElementById(statusMessageId);
		this.stopButton = document.getElementById(stopButtonId);
		this.usernameElement = document.getElementById(usernameId);
		this.videoElement = document.getElementById(videoId);
	}

}


class Manager {
	/**
	 * Creates a new instance of Manager
	 * @constructor
	 * @param {WebPageControls} webPageControls
	 */
	constructor(webPageControls, signingUrl = UrlPaths.PERFORM_SIGN_IN_URL) {

		this.approveAutoSignIn = true;
		this.isStreaming = false;
		this.signingUrl = signingUrl;
		this.videoResolution = VideoResolutionFormatNames.QVGA;
		this.webPageControls = webPageControls;
		this.webPageControls.abortButton.addEventListener("click", this.abortAutoSignIn.bind(this));
		this.webPageControls.stopButton.addEventListener("click", this.stopStreamingVideoToServer.bind(this));
		this.webPageControls.startButton.addEventListener("click", this.streamVideoToServer.bind(this));
	}

	abortAutoSignIn() {
		this.approveAutoSignIn = false;
	}

	/**
	 * Builds the options for the request to upload facial data
	 * @param {String} imageBase64Encoding  The base64 encoding of the image to upload
	 * @param {Number} imageNumber The number of the image being uploaded
	 * @returns {Object} The options for the request
	 */
	buildIdentifyUserOptions(imageBase64Encoding) {
		const formData = new FormData();

		formData.append('image-base64', imageBase64Encoding);

		const options = {
			body: formData,
			method: "POST",
		}
		return options;
	}
	/**
	 * Stop streaming video to the server by setting the isStreaming flag to false and stopping the camera
	 */
	stopStreamingVideoToServer() {
		this.isStreaming = false;
		this.stopCamera();
	}
	/**
	 * Stream video to the server by starting the camera, setting isStreaming flag to True, 
	 * and sending image frames to the server for user identification and potential auto sign-in.
	 */
	async streamVideoToServer() {
		await this.startCamera();
		this.isStreaming = true;

		while (this.isStreaming) {
			await progressCountdown(3, this.webPageControls.autoSignInCountDownElement);

			let imageBase64Encoding = buildImageBase64Encoding(this.webPageControls.videoElement);
			let options = this.buildIdentifyUserOptions(imageBase64Encoding);
			let response = await fetch(UrlPaths.IDENTIFY_USER_FROM_FACE_URL, options);


			if (response.status == ResponseCodes.SUCCESS) {
				let json = await response.json();
				this.displayUserAccount(json);
				let userAccountId = json.userId;
				if (userAccountId != 0) {
					await progressCountdown(5, this.webPageControls.autoSignInCountDownElement);
					if (this.approveAutoSignIn)
						await this.userAutoSign(userAccountId);
					else
						this.approveAutoSignIn = true;
				}
			}
		}
	}

	/**
	 * 
	 * @param {Number} userAccountId 
	 */

	/**
	 * 
	 * @param {Number} userAccountId 
	 */
	/**
	 * Performs an auto sign-in for the user based on the sign-in url
	 * Update the status message element with the appropriate message based on the response status.
	 * @param {Number} userAccountId
	 * 
	 */
	async userAutoSign(userAccountId) {
		let locationId = this.webPageControls.locationField.value;
		let url = `${this.signingUrl}${locationId}/${userAccountId}`;
		let response = await fetch(url);

		let message = getMessage(response.status, this.signingUrl == UrlPaths.PERFORM_SIGN_IN_URL);

		this.webPageControls.statusMessageElement.textContent = message;
	}
	/**
	 * Displays the user account information
	 * @param {Object} userAccountJson 
	 */
	displayUserAccount(userAccountJson) {
		let userAccountId = userAccountJson.userId;
		if (userAccountId == 0) {
			this.webPageControls.detectedUserPanel.classList.add("d-none");
			this.webPageControls.statusMessageElement.textContent = "No user found";
			this.webPageControls.usernameElement.textContent = "";
		}
		else {
			this.webPageControls.detectedUserPanel.classList.remove("d-none");

			//this.webPageControls.userIdElement.textContent = userAccountId;
			this.webPageControls.usernameElement.textContent = userAccountJson.username;
			//this.webPageControls.firstNameElement.textContent = userAccountJson.firstName;
			//this.webPageControls.lastNameElement.textContent = userAccountJson.lastName;
		}
	}


	/**
	 * Starts the camera and displays the video stream without audio on the video element.  If the video element does not exist, it will be created.
	 * @param {VideoResolutionFormatNames} resolution 
	 * @param {String} videoId The HTML element id of the video element to display the video stream on.
	 */
	async startCamera() {
		let webPageControls = this.webPageControls;
		let videoConstraint = VideoResolutionFormats[this.videoResolution];
		if (!videoConstraint) {
			videoConstraint = true;
		}

		await navigator.mediaDevices.getUserMedia({ video: videoConstraint, audio: false })
			.then(function (stream) {
				webPageControls.videoElement.srcObject = stream;
				webPageControls.videoElement.play();
			})
			.catch(function (err) {
				webPageControls.statusMessageElement.textContent = `A Camera error occurred: ${err.name} ${err.message}`;
				console.error(webPageControls.statusMessageElement.textContent);
			});
	}
	/**
	 * Starts the camera and displays the video stream without audio on the video element.  If the video element does not exist, it will be created.
	 * @param {VideoResolutionFormatNames} resolution 
	 * @param {String} videoId The HTML element id of the video element to display the video stream on.
	 */
	async stopCamera() {

	}
}
/**
 * Create a base64 encoding of the image from the video element
 * @param {*} videoElement The video element to capture an image from
 * @returns string the base64 encoding of the image
 */
function buildImageBase64Encoding(videoElement) {
	let canvas = document.createElement("canvas");
	canvas.getContext('2d').drawImage(videoElement, 0, 0, canvas.width, canvas.height);
	return canvas.toDataURL();
}
/**
 * Display a countdown timer for 10 seconds on the given element
 * @param {*} autoSignInCountDownElement The element to display the countdown timer on.
 */
async function fiveSecondTimeOut(autoSignInCountDownElement) {
	const oneSecond = 1_000;
	let seconds = 10;
	let downloadTimer = setInterval(function () {
		if (seconds <= 0) {
			clearInterval(downloadTimer);
			autoSignInCountDownElement.textContent = "Taking Picture";
		} else {
			autoSignInCountDownElement.textContent = seconds + " seconds remaining";
		}
		seconds -= 1;
	}, oneSecond);
}
/**
 * Display a countdown timer on the given element
 * @param {int} seconds The number of seconds for the countdown.
 * @param {*} countDownElement The element to display the countdown timer on.
 * @returns The element to display the countdown timer on.
 */
function progressCountdown(seconds, countDownElement) {
	const oneSecond = 1_000;

	return new Promise((resolve, _) => {
		let countdownTimer = setInterval(() => {
			seconds--;

			countDownElement.textContent = seconds;

			if (seconds <= 0) {
				clearInterval(countdownTimer);
				resolve(true);
			}
		}, oneSecond);
	});
}



const FACE_SAMPLE_COUNT = 30;

/**
 * Asynchronously sets up user facial recognition by capturing and uploading face samples.
 *
 * This function captures a predefined number of face samples from a video input element, then
 * uploads these samples to the server to set up facial recognition for the user. If the face
 * is not detected in the captured frame, it will retry until it reaches the attempt limit.
 * The function updates the status message displayed on the page based on the success or failure
 * of the facial recognition setup.
 */
async function setupUserFacialRecognition() {

	let videoElement = document.getElementById('videoInput');


	document.getElementById("statusMessage").textContent = "Uploading Facial Data, please stand by.";

	let failCount = 0;
	let imageNumber = 1;
	const  ATTEMPT_LIMIT= 900;
	const userAccountId = document.getElementById("user-account-id").value;
	while (imageNumber <= FACE_SAMPLE_COUNT && failCount < ATTEMPT_LIMIT) {

		let imageBase64Encoding = buildImageBase64Encoding(videoElement);

		let options = buildUserFacialRecognitionSetUpOptions(imageBase64Encoding, imageNumber, userAccountId);
		let responseCode = await getResponseCode(UrlPaths.UPLOAD_FACIAL_DATA_URL, options);

		if (responseCode == ResponseCodes.NO_FACE_FOUND){
			failCount++;
			continue;
		}
		else if (responseCode == ResponseCodes.SUCCESS)
			imageNumber++;
		else
			break;
	}

	if(imageNumber >= FACE_SAMPLE_COUNT)
		document.getElementById("statusMessage").textContent = "Facial Data Uploaded Successfully";
	else
		document.getElementById("statusMessage").textContent = "An error occurred while uploading facial data, please try again later.";
}

/**
 * Build the request options for the user facial recognition setup
 * @param {String} imageBase64Encoding The base64 encoded image
 * @param {int} imageNumber The image number
 * @param {*} userAccountId The user account id
 * @returns The request options including body and method.
 */
function buildUserFacialRecognitionSetUpOptions(imageBase64Encoding, imageNumber, userAccountId) {
	const formData = new FormData();

	formData.append('image-base64', imageBase64Encoding);
	formData.append('image-number', imageNumber);
	formData.append('user-account-id', userAccountId);

	const options = {
		body: formData,
		method: "POST",
	}
	return options;
}
/**
 * Asynchronously streams the sign-out video to the server and handles the response.
 * Alerts the user with the sign-out status message.
 */
async function streamSignOutVideo() {
	let responseCode = await streamRoasterSigningVideo(UrlPaths.PERFORM_SIGN_OUT_URL);
	let message = getMessage(responseCode, false);
	alert(message);
}
/**
 * Handles the stop button click event by setting isStreaming to false,
 * disabling the stop button, and enabling the access control button.
 */
function stopButtonOnClick() {
	isStreaming = false;
	getStopButton().disabled = true;
	getAccessControl().disabled = false;
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
async function getResult(url, options) {
	let responseCode;
	let json;
	await fetch(url, options)
		.then(function (response) {
			json = response.json()
			responseCode = response.status;
		})
		.catch(function (err) {
			responseCode = ResponseCodes.ERROR;
		});
	return json;
}
/**
 * Updates the status message on the web page with the provided message.
 * @param {string} message - The message to display as the status message.
 */
function display(message) {
	getStatusMessageControl().textContent = message;
}
/**
 * Waits for 5 seconds before resolving the Promise.
 * @returns {Promise} A Promise that resolves after a 5-second delay.
 */
async function FiveSecondTimeOut() {
	const fiveSeconds = 5000;
	await new Promise(handler => setTimeout(handler, fiveSeconds));
}

/**
 * Streams the video from the webcam to the server to be processed for signing on/off the roaster
 * @param {String} url The url to send the request to
 * @returns A Response Code
 */
async function streamRoasterSigningVideo(url) {

	let videoElement = document.getElementById('videoInput');
	let imageNumber = 0;
	const locationId = document.getElementById("location-id").value;

	const csrfToken = "";//document.querySelector('[name=csrfmiddlewaretoken]').value;
	let responseCode;
	do {

		let imageBase64Encoding = buildImageBase64Encoding(videoElement);
		let options = buildSignInOptions(imageBase64Encoding, imageNumber, locationId, csrfToken);
		responseCode = await getResponseCode(url, options);

		await waitFiveSeconds();
	}
	while (responseCode == MyResponseCodes.NO_FACE_FOUND)
	return responseCode;
}


/**
 * Returns a message string based on the given response code and whether the user is signing in or out.
 * @param {number} responseCode - The response code from the server.
 * @param {boolean} signOn - True if the user is signing in, false if signing out. Default is true.
 * @returns {string} A message corresponding to the given response code.
 */
function getMessage(responseCode, signOn = true) {
	if (responseCode == ResponseCodes.SUCCESS) {
		if (signOn)
			return "Sign in completed";
		else
			return "Sign out completed";
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
 * Returns a "go" or "stop" message based on the given response code.
 * @param {number} responseCode - The response code from the server.
 * @returns {string} "go" if the response code indicates successful access control, otherwise "stop".
 */
function getAccessControlMessage(responseCode) {
	if (responseCode == ResponseCodes.SUCCESS) {
		return "go";
	}
	else if (responseCode == MyResponseCodes.ALREADY_ON_ROASTER)
		return "stop";
	else if (responseCode == MyResponseCodes.LOCATION_PERMISSION_DENIED)
		return "stop";
	else if (responseCode == MyResponseCodes.NOT_ON_ROASTER)
		return "stop";
	else if (responseCode >= 500) //500+ are server errors
		return `stop`;

	return `stop`;
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
