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