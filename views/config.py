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

# FB_SERVICE_ACCOUNT = {
#   "type": "service_account",
#   "project_id": "andsnews",
#   "private_key_id": "0cc02e5e78adb13b29a23a1e08c51a033864e355",
#   "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCv55grR64tm0D1\nGJyyV6GEkxVT/aZRE2JOkXG5IRREJw96AbJVzZUFuzQzKKKktUCpXO3rsrC8es8f\n2JXPuyG/NewKVwl5JnddJeLigaGZwNozhpGA+P76ZCzVnTUdikdGRgknwwWPlhfp\nEwmSiLw8lR8FCFnaf6ylvlf/l2iwy/JdWz05V9/fdIPJr4JOsFjWZ9mS7vckwQGc\n+bux16zQvKi5i+/faMD4zq7OTgSh7m9maWl1ZizGBkgoHHxHqd0vEOZPRoBQAJ6h\npptkD25MTGn3gaIsuq6P6iwT7d2xkYDFkfZEnAyGhIrp7N8DgP2LrmFZcSi7ZpWg\n7UsBmeOTAgMBAAECggEAcIzhy4eAxgOZq3lFAcOaQCaQNf6NBUE+3ICpYEfvHLBV\ncb5WKhpxaIpgmv88GeEzb2pbfT0HYoG9t2WwbYsRy7OnxPHtyMu5Aiu0oTNKgANq\nWh+XSAuJshKYsVF2Y+FPO4KiZwOcskPaJrKcpFrC/ox3nZO7Ulfw0tgYnBx3yu6T\n5vyz2CZBpEi3Q6o4U9ZXG8owxRxJIY9yUAY4QjvSOEW/3/qRAg6IPtT3/HkS4yhE\nKy+/FWMUDMcxUnbT7V55h4FyrbufJMTDElmJtA0eZ/bGVIzcA9T47f3YRxalFGTX\nH9F5hPDZTPIdzjHozh16AWz3mRT5p7jf2ELsz7+0eQKBgQDdV+penBpo0iYBrKMN\nwO1ID1GEc5J8jjzd9Y+UjiKVqPzimi3tYoSpPbOMRJJjpBaWfm8t1DbricuzGJL+\nmbNNtYm4Q0x7jXArlmJSCwQ0A8NxBvU0nAUOJCN6ImWXZHFbODwjGtz29a7/3Gai\njSWd8chIBUgTE9jqzD3o7nCaxQKBgQDLcly5ZKDGpscKpJHwztliuufuZ4iwi3Au\n0SzxUkNxi4RPf5XHXQtMCT4GpdVx0rd26ZPWrtpG6F0AY2Z1S9RLOKBM/FcHVwzS\nKjvLTpZNZ1PTqSGhUz0RJ92izbVzTpKsQq+gg35SOE83hctNQckGMcKijl4xgdun\nqVdWMMFKdwKBgCwFUh1i2nXCZcCrfvo7RnWwZjv7aETRXRWfwuB+rC4rn6/JjhzK\nHSwzk0PwV1Tty3g+yQnKTOnnS9Xgq0trchegZTV6XPmtlYN1szQx8LIPlY0jHx1J\nck/vrAacVKwZU9oagwtQSmXrUtScFuV5QOP6tCRuuHji159K430x/r8pAoGBAJ6n\nnK/nTYodXXNrS3Rjmxtnbp94lhw3YVDhRw8afAX8Kz5j3MYQRVMSkhBVGtMc5H4T\nQXtV+Fr7sisvWSN38yKGElx3HNdYh2MOFHtD2eqa/cA+UT+hzimm0Sy5BxvY1oEH\nsDaY1NYBm6VM7XJeLwppm8NxCvvIrSde5AEPHG2ZAoGAHMWxT1HC7SP/wDcJiOrX\nicBGUxcrdqd8wFg8jJr8x7p4EE5WM0Y6neFI1SK1lo07hGvMcBdgJNGyeFlRycpj\nxeKTuc+S0NJiUMgz1g4QoLOz29unoiHbOWpfFVLFL7l8d+yJlSj0CO5ki1/XVzzk\njUEz4X4ixYIE59WUas1LJVA=\n-----END PRIVATE KEY-----\n",
#   "client_email": "fb-service-account-for-andsnew@andsnews.iam.gserviceaccount.com",
#   "client_id": "115654535457758416318",
#   "auth_uri": "https://accounts.google.com/o/oauth2/auth",
#   "token_uri": "https://accounts.google.com/o/oauth2/token",
#   "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
#   "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/fb-service-account-for-andsnew%40andsnews.iam.gserviceaccount.com"
# }

SERVICE_ACCOUNT = 'andsnews@appspot.gserviceaccount.com'

BUCKET = '/' + os.environ.get('BUCKET_NAME', app_identity.get_default_gcs_bucket_name())
DEVEL = os.environ.get('SERVER_SOFTWARE', '').startswith('Devel')
START_MSG = '*** START ***'
END_MSG = '*** END ***'

COLOR_NAMES = (
    'red', 'orange', 'yellow', 'green', 'blue', 'violet', 'dark', 'medium', 'light'
)
# http://www.color-blindness.com/color-name-hue/
HUE = [
    {'span': range(306, 360) + range(13), 'order': '0', 'name': 'red',    'hex': '#c00'},
    {'span': range(13, 42),               'order': '1', 'name': 'orange', 'hex': '#f90'},
    {'span': range(42, 70),               'order': '2', 'name': 'yellow', 'hex': '#ff0'},
    {'span': range(70, 167),              'order': '3', 'name': 'green',  'hex': '#0c0'},
    {'span': range(167, 252),             'order': '4', 'name': 'blue',   'hex': '#06f'},
    {'span': range(252, 306),             'order': '5', 'name': 'violet', 'hex': '#c0c'}
]
LUM = [
    {'span': range(0, 15),                'order': '6', 'name': 'dark',   'hex': '#111'},
    {'span': range(15, 70),               'order': '7', 'name': 'medium', 'hex': '#555'},
    {'span': range(70, 101),              'order': '8', 'name': 'light',  'hex': '#ccc'}
]
SAT = [
    {'span': range(0, 6),                               'name': 'monochrome'},
    {'span': range(6, 101),                             'name': 'color'}
]
COLORS = HUE + LUM

ASA = [50, 64, 80, 100, 125, 160, 200, 250, 320, 400, 500, 640, 800,
       1000, 1250, 1600, 2000, 2500, 3200, 4000, 5000, 6400]

# < /dev/urandom tr -dc _A-Z-a-z-0-9 | head -c${1:-32};echo;
