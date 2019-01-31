import os
from base64 import b64encode
import flask

import googleapiclient.discovery
from oauth2client.client import GoogleCredentials

app = flask.Flask(__name__)

# Settings
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_FILE = "credentials.json"


@app.route("/")
def index():
    return flask.render_template("index.html")

@app.route("/upload", methods=['POST'])
def upload():
    # uploads and saves
    target = os.path.join(APP_ROOT, "images/")

    if not os.path.isdir(target):
        os.mkdir(target)

    try:
        file = flask.request.files['photo']
        destination = "/".join([target, file.filename])
        file.save(destination)

        result = google_vision_processor(file.filename)

        return flask.render_template("complete.html", result=result)

    except KeyError:
        return flask.render_template("incomplete.html")


def google_vision_processor(file):
    # Connect to the Google Cloud-ML Service
    credentials = GoogleCredentials.from_stream(CREDENTIALS_FILE)
    service = googleapiclient.discovery.build('vision', 'v1', credentials=credentials)

    IMAGE_FILE = "images/{}".format(file)
    # Read file and convert it to a base64 encoding
    with open(IMAGE_FILE, "rb") as f:
        image_data = f.read()
        encoded_image_data = b64encode(image_data).decode('UTF-8')

    # Create the request object for the Google Vision API
    batch_request = [{
        'image': {
            'content': encoded_image_data
        },
        'features': [
            {
                'type': 'LABEL_DETECTION'
            }
        ]
    }]
    request = service.images().annotate(body={'requests': batch_request})

    # Send the request to Google
    response = request.execute()

    # Check for errors
    if 'error' in response:
        raise RuntimeError(response['error'])

    # Print the results
    labels = response['responses'][0]['labelAnnotations']

    for label in labels:
        if (label['description'] == 'Cat'):
            prediction = "Chance that Cat is present in this image is {}%.".format(label['score']*100)
            break
        else:
            prediction = "No Cat is present"

    return prediction

if __name__ == "__main__":
    app.run()
