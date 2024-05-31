document.addEventListener("DOMContentLoaded", function () {
    var form = document.getElementById('commandForm');
    var submitBtn = document.getElementById('submitBtn');
    var errorContainer = document.getElementById('errorContainer');

    form.addEventListener('submit', function (event) {
        event.preventDefault(); // Prevent default form submission

        // Clear previous error messages
        errorContainer.textContent = '';
        errorContainer.classList.remove('alert', 'alert-danger', 'alert-dismissible');

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
                errorContainer.textContent = response.error || 'An error occurred while submitting the command';
                errorContainer.classList.add('alert', 'alert-danger', 'alert-dismissible');
            }
        };

        // Define what happens in case of error
        xhr.onerror = function () {
            errorContainer.textContent = 'An error occurred while submitting the command';
            errorContainer.classList.add('alert', 'alert-danger', 'alert-dismissible');
        };

        // Open connection
        xhr.open('POST', form.action);

        // Send form data
        xhr.send(formData);
    });
});