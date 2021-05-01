import main
import unittest
import requests
from .config import CONFIG

HEADERS = {
    'Authorization': f'key={CONFIG["fcm_server_key"]}',
    'Content-Type': 'application/json',
}


class TestApp(unittest.TestCase):
    def setUp(self):
        self.client = main.app.test_client()

    def test_send(self):
        # auth.fetchToken
        token = "eDMO6WOdrfOYUkDm-OK50Q:APA91bEduZHTu3YMGuqaYHNGafFoXfVwXV5AlbEmWO4p5vvOX1jaj4KxsQ3b6stz_akLyqXNFuP7ZHzEI7Mx_C3ceAfrYyafk-oI_E9iEc0FhAlu_yFaGrqJJ68p24MeeXWPW5z6ffQp"
        payload = {
            "to": token,
            "notification": {
                "title": "ands",
                "body": 'done.'
            }
        }
        response = requests.post(
            CONFIG['fcm_send'], json=payload, headers=HEADERS)
        print(response.json())


# no need to run server!
# (andsnews) $ python -m unittest api/test_firebase.py
