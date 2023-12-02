import os
from flask import Flask, request, render_template

# Import necessary modules
import requests

# Create a Flask web application
app = Flask(__name__, static_folder='static')

# Autoderm API URL
API_URL = "https://autoderm.firstderm.com/v1/query"

# Replace 'YOUR_API_KEY' with your actual API key (first derm)
API_KEY = ""
# Static information about skin diseases (description, symptoms, and treatment)
disease_info_data = {
    'Vitiligo': {
        'description': 'Vitiligo is depigmentation of the skin. It causes the skin to lose color, and patches of lighter skin appear. This happens when the melanocytes (skin pigmentation cells) die or cannot function. It is not contagious or dangerous.',
        'symptoms': 'Small white patches of depigmentation can signify vitiligo. This usually occurs in areas where the skin is most exposed to the sun, such as around the face, feet, arms, hands, and lips. Sometimes it also appears in armpits, rectal areas and the genitalia.',
        'treatment': 'Although not preventable or curable, common treatments include skin exposure to UVB lamps and skin grafting (skin transplantation). Other medical methods include topical creams, oral medication, and removing color from other skin areas to match the color of the white patches. Some people prefer tattooing small areas of the skin or using cosmetics to cover up the patches. These medicines have possible side effects, so patients must be carefully monitored.',
        'image_filename': 'acne.jpg'
    },
    'Atopic Eczema': {
        'description': 'Atopic eczema can be caused by sensitivity to certain food, such as dairy products, eggs or fish. Infants with food allergies often have hives in the eczema. The child also may also experience atopic symptoms from the respiratory system (asthma) and stomach discomfort.',
        'symptoms': 'Red, thickened, itchy patches on the skin are symptoms of atopic eczema. It usually appears when the child is around one year’s old. ',
        'treatment': 'In this case, you may need treatment with oral antiviral treatment. Topical steroids should not be used.',
        'image_filename': 'atopic_eczema.jpg'
    },
    'Psoriasis': {
        'description': 'Psoriasis is a skin disease that presents as red, flakey, and sometimes itchy blotches. Common signs of psoriasis are red, scaly patches on distinct parts of the body such as the elbows and knees. Skin folds such as groin, armpits, nails and the scalp may be affected as well.',
        'symptoms': 'The most common form of psoriasis appears as round and scaly rash, called plaque. The size is usually a few centimeters. Plaque psoriasis can appear anywhere on the body, but most often on elbows, knees, lower back and scalp. Plaque psoriasis is usually symmetrical on both sides of the body (e.g. in the same place on both right and left elbow). New rash may itch a lot and often turns into scars or wounds.',
        'treatment': 'If symptoms are mild then simple emollients and avoiding soap may help. Ointment or cream containing salicylic acid for example, or urea can also help to reduce scaling. If you have moderate to severe symptoms, regular treatment may be needed, such as prescription creams or light therapy. ',
        'image_filename': 'psoriasis.jpg'
    },
    'Pityriasis Versicolor': {
        'description': 'Pityriasis versicolor is a superficial fungal infection caused by the skin yeast, Malassezia furfur. The fungus is found on the skin surface of most adults and thrives in warm and moist environment, especially on oily skin.',
        'symptoms': 'Pityriasis versicolor causes discrete hyperpigmented, orangey, scaly patches. This is because it often causes sharply defined spots that gather together to form large patches on the skin. Sometimes, these spot can also be brownish and scaly. It is usually located on areas with a lot of sebaceous and sweat glands, such as the chest and back.',
        'treatment': 'Topical anti-yeast shampoos, such as Oliatum scalp shampoo, Selsum shampoo, and Nizoral shampoo, tend to work well to treat pityriasis versicolor. They can either be applied directly to the skin overnight (although this may cause irritation), or used daily in the shower. You should leave it on the skin for 5 minutes before rinsing. Continue treatments long term to reduce recurrence for 6-12 months. For smaller areas, ketoconazole 2% cream is a also good option. It is important to treat the entire upper body and arms even if lesions are not looking so prevalent out. The risk of relapse is high and you should start a treatment again.',
        'image_filename': 'pityriasis_versicolor.jpg'
    },
    'Atypical Melanocytic Nevus': {
        'description': 'Moles are brown, round, raised and sometimes hairy birthmarks that usually do not disappear by themselves over time. They are usually harmless but it is important to keep track of the changes. They can be removed if they are bothersome, unsightly or if they start to change shape, size or color.',
        'symptoms': 'Moles usually do not cause symptoms, but changes in size, shape, or color should be monitored.',
        'treatment': 'Treatment is typically not required unless there are signs of abnormal changes.',
        'image_filename': 'melanocytic_nevus.jpg'
    },
    'Ajhyg': {
        'description': 'Moles are brown, round, raised and sometimes hairy birthmarks that usually do not disappear by themselves over time. They are usually harmless but it is important to keep track of the changes. They can be removed if they are bothersome, unsightly or if they start to change shape, size or color.',
        'symptoms': 'Moles usually do not cause symptoms, but changes in size, shape, or color should be monitored.',
        'treatment': 'Treatment is typically not required unless there are signs of abnormal changes.',
        'image_filename': 'melanocytic_nevus.jpg'
    },

    'Contact Dermatitis': {
        'description': 'Contact dermatitis is a rash or irritation of the skin caused by contact with a foreign substance. The inflammation only occurs on the superficial regions of the skin. Common causes are poison oak, latex, perfumes, detergents, and certain foods. UV light can also be a cause.',
        'symptoms': 'It causes large, itchy rashes on the skin exposed to the irritant. The rash is red and appears within a day after contact. It can also form cracks, blisters and hives. The rash can last for weeks. The symptoms often get worse when you scratch the affected area.',
        'treatment': 'The rash will usually fade after a few days if you stop any contact with the irritant. Cold compresses can reduce blistering, and antihistamines relieve itching. If the rash spreads or does not improve after a few days, consult a physician. You may be prescribed corticosteroids or antihistamines which can reduce inflammation. Sometimes you need a stronger cortisone cream.',
        'image_filename': 'contact_dermatitis.jpg'
    },
    'Nevus (Benign Mole)': {
        'description': 'Dermatitis is a general term that describes inflammation of the skin...',
        'symptoms': 'Symptoms may include itching, rash, and...',
        'treatment': 'Treatment involves identifying and avoiding triggers, along with...',
        'image_filename': 'benign_mole.jpg'
    },
    # Add more diseases as needed
}
# Define a route for the root URL ("/") that handles both GET and POST requests
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

        # Print the entire response for debugging
        print(response.text)

        # Get the JSON data returned by the Autoderm API
        data = response.json()

        # Check if 'predictions' key exists in the response
        if "predictions" in data:
            predictions = data["predictions"]

            # Add static disease information, symptoms, and treatment to predictions
            for prediction in predictions:
                disease_name = prediction.get('name')
                if disease_name in disease_info_data:
                    disease_info = disease_info_data[disease_name]
                    prediction['disease_info'] = disease_info['description']
                    prediction['symptoms'] = disease_info['symptoms']
                    prediction['treatment'] = disease_info['treatment']
                    prediction['image_filename'] = disease_info['image_filename']
                else:
                    prediction['disease_info'] = 'No additional information available.'
                    prediction['symptoms'] = 'No information available.'
                    prediction['treatment'] = 'No information available.'
                    prediction['image_filename'] = 'default_image.jpg'

            return render_template("index.html", predictions=predictions)

        # Handle case where 'predictions' key is not present in the API response
        return render_template("index.html", error="No predictions in the API response")

    # Handle GET request
    return render_template("index.html")
# Helper function to check if a file has an allowed extension
def allowed_file(filename, allowed_extensions):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions

# Run the Flask application if this script is executed directly
if __name__ == "__main__":
    app.run(debug=True, port=8080)
