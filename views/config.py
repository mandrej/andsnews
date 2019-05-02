import os
from google.appengine.api import app_identity

FIREBASE = {
    "apiKey": "AIzaSyBj5uKo0P_mir_ChQ_syx_kUQ_g7nkNy6M",
    "authDomain": "andsnews.firebaseapp.com",
    "databaseURL": "https://andsnews.firebaseio.com",
    "storageBucket": "andsnews.appspot.com",
    "messagingSenderId": "719127177629",
    "messagingServerKey": "AAAAp29R6Z0:APA91bEsmfN6-ZywxP05Xpw-Ooto5FwTyXjgxRcqDllaTo6Kay3y8wnB-1QcwBt1-iQvoPt2p8wwp0JmKz4xWHST-pAQyrAivyTT-RFXasRYGmT09rP6oMuW95XHEi-HANZgzljuA-4i4Gh44den43zooddq5uSjBA"
}

SERVICE_ACCOUNT = 'andsnews@appspot.gserviceaccount.com'

BUCKET = '/' + os.environ.get('BUCKET_NAME', app_identity.get_default_gcs_bucket_name())
DEVEL = os.environ.get('SERVER_SOFTWARE', '').startswith('Devel')
START_MSG = '*** START ***'
END_MSG = '*** END ***'

PHOTO_FILTER = ['year', 'tags', 'model', 'nick']
LIMIT = 24
PERCENTILE = 80

ASA = [50, 64, 80, 100, 125, 160, 200, 250, 320, 400, 500, 640, 800,
       1000, 1250, 1600, 2000, 2500, 3200, 4000, 5000, 6400]

# < /dev/urandom tr -dc _A-Z-a-z-0-9 | head -c${1:-32};echo;
