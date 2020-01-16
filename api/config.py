import os
FIREBASE = {
    "apiKey": "AIzaSyBj5uKo0P_mir_ChQ_syx_kUQ_g7nkNy6M",
    "authDomain": "andsnews.firebaseapp.com",
    "databaseURL": "https://andsnews.firebaseio.com",
    "storageBucket": "andsnews.appspot.com",
    "messagingSenderId": "719127177629",
    "messagingServerKey": "AAAAp29R6Z0:APA91bEsmfN6-ZywxP05Xpw-Ooto5FwTyXjgxRcqDllaTo6Kay3y8wnB-1QcwBt1-iQvoPt2p8wwp0JmKz4xWHST-pAQyrAivyTT-RFXasRYGmT09rP6oMuW95XHEi-HANZgzljuA-4i4Gh44den43zooddq5uSjBA"
}

DEVEL = os.environ.get('WERKZEUG_RUN_MAIN') == 'true'
START_MSG = '*** START ***'
END_MSG = '*** END ***'

PHOTO_FILTER = ['year', 'tags', 'model', 'email']
LIMIT = 24

ASA = [50, 64, 80, 100, 125, 160, 200, 250, 320, 400, 500, 640, 800,
       1000, 1250, 1600, 2000, 2500, 3200, 4000, 5000, 6400]
