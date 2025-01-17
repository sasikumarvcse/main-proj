document.getElementById("uploadForm").addEventListener("submit", function (event) {
    event.preventDefault();

    const formData = new FormData(this);
    const progressDiv = document.getElementById("progress");
    const submitButton = document.getElementById("submitBtn");
    const fileInput = document.getElementById("fileInput");
    const resultsDiv = document.getElementById("results");
    const backHomeBtn = document.getElementById("backHomeBtn");

    // Show the progress indicator, hide file input, and disable the button
    progressDiv.classList.remove("hidden");
    fileInput.classList.add("hidden");
    submitButton.disabled = true;

    fetch("/upload", {
        method: "POST",
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            const nutrition = data.nutrition;

            // Create a table for the nutrition summary
            const nutritionTable = `
                <table class="nutrition-table">
                    <tbody>
                        <tr>
                            <td>Total Calories</td>
                            <td>${nutrition.total_calories} kcal</td>
                        </tr>
                        <tr>
                            <td>Carbs</td>
                            <td>${nutrition.macros.Carbs} g</td>
                        </tr>
                        <tr>
                            <td>Protein</td>
                            <td>${nutrition.macros.Protein} g</td>
                        </tr>
                        <tr>
                            <td>Fat</td>
                            <td>${nutrition.macros.Fat} g</td>
                        </tr>
                        <tr>
                            <td>Fiber</td>
                            <td>${nutrition.macros.Fiber} g</td>
                        </tr>
                        <tr>
                            <td>Potassium</td>
                            <td>${nutrition.micros.Potassium} mg</td>
                        </tr>
                        <tr>
                            <td>Vitamin C</td>
                            <td>${nutrition.micros["Vitamin C"]} mg</td>
                        </tr>
                    </tbody>
                </table>
            `;

            resultsDiv.innerHTML = `
                <div class="card">
                    <h3>Detected Items:</h3>
                    <p>${data.detections.join(", ")}</p>
                </div>
                <div class="card">
                    <h3>Nutrition Details:</h3>
                    ${nutritionTable}
                </div>
            `;

            // Show the results and the Back to Home button
            resultsDiv.classList.remove("hidden");
            backHomeBtn.classList.remove("hidden");

            // Hide the progress indicator and enable the button again
            progressDiv.classList.add("hidden");
            submitButton.disabled = false;
        })
        .catch(error => {
            console.error("Error:", error);
            // Hide the progress indicator and enable the button in case of an error
            progressDiv.classList.add("hidden");
            submitButton.disabled = false;
        });
});

function goHome() {
    // Reset all elements to their initial state
    document.getElementById("uploadForm").reset();  // Resets the form (file input)
    document.getElementById("fileInput").classList.remove("hidden");  // Show the file input again
    document.getElementById("submitBtn").disabled = false;  // Enable the submit button
    document.getElementById("results").classList.add("hidden");  // Hide results
    document.getElementById("backHomeBtn").classList.add("hidden");  // Hide the back button
    document.getElementById("progress").classList.add("hidden");  // Hide progress indicator
}
