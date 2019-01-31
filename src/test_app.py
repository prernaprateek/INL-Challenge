import pytest
import re, os, shutil
from app import app, google_vision_processor

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

@pytest.fixture
def client(request):
    app.testing = True
    test_client = app.test_client()

    def teardown():       # databases and resources have to be freed at the end. Only "image" directory needs to be wiped off
        shutil.rmtree(os.path.join(APP_ROOT, "images/"))

    request.addfinalizer(teardown)
    return test_client


class TestApp():
    def test_when_no_photo(self, client):
        response = client.post("/upload")
        result = response.data
        assert bool(re.search("You Forgot to select Photo", str(result))) == True

    def test_when_photo(self, client, mocker):
        gvp_mock = mocker.patch("app.google_vision_processor")
        gvp_mock.return_value = "XYZ"  # Anything Arbitrary

        asset = "catpp661u.jpg"
        APP_ROOT = os.path.dirname(os.path.abspath(__file__))
        file = os.path.join(APP_ROOT, f"{asset}")

        response = client.post("/upload",
                               data={
                                   'photo': (file, asset)
                               }
                               )
        result = response.data
        assert bool(re.search("Processing Done!!", str(result))) == True

    def test_when_cat_photo_int(self, client):
        asset = "catpp661u.jpg"
        file = os.path.join(APP_ROOT, f"{asset}")

        response = client.post("/upload",
                               data={
                                   'photo': (file, asset)
                               }
                               )
        result = response.data
        assert bool(re.search("Chance that Cat is present in this image is", str(result))) == True

    def test_when_not_cat_photo_int(self, client):
        asset = "road_sign.jpg"
        APP_ROOT = os.path.dirname(os.path.abspath(__file__))
        file = os.path.join(APP_ROOT, f"{asset}")

        response = client.post("/upload",
                               data={
                                   'photo': (file, asset)
                               }
                               )
        result = response.data
        assert bool(re.search("No Cat is present", str(result))) == True
