import main
import unittest
import warnings
import firebase_admin
from datetime import datetime
from firebase_admin import credentials, initialize_app, delete_app, messaging, exceptions


class TestApp(unittest.TestCase):
    def setUp(self):
        # self.client = main.app.test_client()
        try:
            self.app = firebase_admin.get_app()
        except ValueError as e:
            print('NEW INSTANCE')
            cred = credentials.Certificate('credentials.json')
            self.app = initialize_app(cred)

    def test_credetial(self):
        warnings.filterwarnings(
            action="ignore", message="unclosed", category=ResourceWarning)
        token, expiry = self.app.credential.get_access_token()
        diff = (datetime.now() - expiry).total_seconds()
        print(f'{token}\n\n{diff}')
        print(self.app.name)  # '[DEFAULT]
        print(self.app.project_id)  # andsnews

    def test_send(self):
        warnings.filterwarnings(
            action="ignore", message="unclosed", category=ResourceWarning)
        message = messaging.Message(
            notification=messaging.Notification(title="ands", body='TEST FCM'),
            token="ftvVMeat-bV2Q275MrGEAu:APA91bH8BH6bSBci-xurGKZFQ3OZZx2hLePg9E1518mr-cVkKbFqhOHir_-Rr1XyY0nGxSOixG3OzqjzRqKy2SsrUJuJgNjqw6yOg2Z9wJnonWDncN9QMjE5LxtNqzTnqusuZjjFZlkm"
        )
        try:
            response = messaging.send(message, app=self.app)
        except exceptions.FirebaseError as e:
            response = e

        # projects/andsnews/messages/0:1620404962628202%2fd9afcdf9fd7ecd
        # projects/andsnews/messages/1dd8b5ba-efdc-4d87-af7b-29f55cbf3082
        print(response)

    def tearDown(self):
        delete_app(self.app)


# no need to run server!
# (andsnews) $ python -m unittest api/test_firebase.py
