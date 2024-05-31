document.addEventListener("DOMContentLoaded", function () {
    var form = document.getElementById('commandForm');
    var submitBtn = document.getElementById('submitBtn');
    var errorContainer = document.getElementById('errorContainer');
    var dismissButton = errorContainer.querySelector('.close');

    form.addEventListener('submit', function (event) {
        event.preventDefault(); // Prevent default form submission

        // Clear previous error messages
        errorContainer.innerHTML = ''; // Clear previous error messages);

        // Get form data
        var formData = new FormData(form);

        // Create XMLHttpRequest object
        var xhr = new XMLHttpRequest();

        // Define what happens on successful data submission
        xhr.onload = function () {
            if (xhr.status === 200) {
                // Handle success, if needed
                console.log("Command submitted successfully");
            } else {
                // Handle error, if needed
                console.log("Error occurred while submitting command");
                // Handle error, display the error message
                var response = JSON.parse(xhr.responseText);
                var errorMessage = response.error || 'An error occurred while submitting the command';
                // Show the dismissable button
                errorContainer.innerHTML = '<div class="alert alert-danger alert-dismissible" role="alert">' + errorMessage + '<button type="button" class="close" data-dismiss="alert">&times;</button></div>';

            }
        };

        // Define what happens in case of error
        xhr.onerror = function () {
            errorContainer.innerHTML = '<div class="alert alert-danger alert-dismissible" role="alert">An error occurred while submitting the command<button type="button" class="close" data-dismiss="alert">&times;</button></div>';
        };

        // Open connection
        xhr.open('POST', form.action);

        // Send form data
        xhr.send(formData);
    });
});