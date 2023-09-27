import os
from flask import Flask, request, render_template, jsonify
import requests  # Import the 'requests' library

app = Flask(__name__)

# Autoderm API URL
API_URL = "https://autoderm.firstderm.com/v1/query"

# Replace 'YOUR_API_KEY' with your actual API key
API_KEY = ""

@app.route("/", methods=["GET", "POST"])
def upload_and_predict():
    if request.method == "POST":
        # Check if a file was uploaded
        if "file" not in request.files:
            return render_template("index.html", error="No file part")

        file = request.files["file"]

        # Check if the file has a filename
        if file.filename == "":
            return render_template("index.html", error="No selected file")

        # Check if the file is allowed (you can add more file extensions)
        allowed_extensions = {"jpg", "jpeg", "png", "gif"}
        if not allowed_file(file.filename, allowed_extensions):
            return render_template("index.html", error="Invalid file extension")

        # Send the image to Autoderm API
        image_contents = file.read()
        response = requests.post(
            API_URL,
            headers={"Api-Key": API_KEY},
            files={"file": image_contents},
            params={"language": "en", "model": "autoderm_v2_0"},
        )

        # Get the JSON data returned
        data = response.json()

        # Get only the predictions
        predictions = data["predictions"]

        return render_template("index.html", predictions=predictions)

    return render_template("index.html")

def allowed_file(filename, allowed_extensions):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions

if __name__ == "__main__":
    app.run(debug=True, port=8080)
