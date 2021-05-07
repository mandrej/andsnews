import main
import unittest
import warnings
import firebase_admin
from datetime import datetime
from firebase_admin import credentials, initialize_app, delete_app, messaging


class TestApp(unittest.TestCase):
    def setUp(self):
        # self.client = main.app.test_client()
        try:
            self.app = firebase_admin.get_app()
        except ValueError as e:
            print('22 NEW INSTANCE')
            cred = credentials.Certificate('credentials.json')
            self.app = initialize_app(cred)

    def test_credetial(self):
        warnings.filterwarnings(
            action="ignore", message="unclosed", category=ResourceWarning)
        token, expiry = self.app.credential.get_access_token()
        diff = (datetime.now() - expiry).total_seconds()
        print(f'{token}\n{diff}')
        # print(self.app.name)
        # print(self.app.project_id)
        # print(credential.valid)

    def test_send(self):
        warnings.filterwarnings(
            action="ignore", message="unclosed", category=ResourceWarning)
        message = messaging.Message(
            notification=messaging.Notification(title="ands", body='TEST'),
            token="d8F8Ow6CS9xY-Uvj5_aaDO:APA91bHG-PPYJzrZxAZN0Dl-en4mBZebGKpwQEklknmi6di1D0fuwiG54P9HInn0j3J8XEsyLIR2nAzAdFuesfxHpgNhO7OlD8LczBmY6D6Hv2cOIgF9ZCEzfte9hb_NDdMRVEVYGtXw"
        )
        response = messaging.send(message, app=self.app)
        # projects/andsnews/messages/0:1620404962628202%2fd9afcdf9fd7ecd
        print(response)

    def tearDown(self):
        delete_app(self.app)


# no need to run server!
# (andsnews) $ python -m unittest api/test_firebase.py
