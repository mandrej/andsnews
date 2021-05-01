import main
import unittest
import firebase_admin
from firebase_admin import credentials, initialize_app, delete_app, messaging


class TestApp(unittest.TestCase):
    def setUp(self):
        self.client = main.app.test_client()
        try:
            self.app = firebase_admin.get_app()
        except ValueError as e:
            print('NEW INSTANCE')
            cred = credentials.Certificate('credentials.json')
            self.app = initialize_app(cred)

    def test_credetial(self):
        credential = self.app.credential.get_credential()
        print(self.app.name)
        print(self.app.project_id)
        print(credential.valid)

    def test_send(self):
        message = messaging.Message(
            notification=messaging.Notification(title="ands", body='TEST'),
            token='eEU5j_cXssNHwCUf68Kzg1:APA91bF1P8viIjC-LV6TN99lGZ6qTG7wOUkcYrshTuHEyRPnbCMsFvQgA1F4-kljSLjHP7Lo1BJCfEEDW7qHR-eMGKimK-pIutHOD88ZbgJHUbTtpv8Dvgy4HByC1SQ1rs40RbcDJh0K'
        )
        response = messaging.send(message, app=self.app)
        print(response)

    def tearDown(self):
        delete_app(self.app)


# no need to run server!
# (andsnews) $ python -m unittest api/test_firebase.py
