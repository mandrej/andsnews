from flask import abort, make_response
from firebase_admin import credentials, initialize_app, messaging

cred = credentials.Certificate('credentials.json')
DEFAULT_APP = initialize_app(cred)
HOSTS = 'https://ands.appspot.com, http://localhost:8080'


def send(request):
    """
    projects/andsnews/messages/0:1620404962628202%2fd9afcdf9fd7ecd
    """
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': HOSTS,
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)

    request_json = request.get_json(silent=True)

    if request_json and 'recipients' in request_json:
        recipients = request_json['recipients']
    else:
        recipients = None
    if request_json and 'message' in request_json:
        message = request_json['message']
    else:
        message = ''

    if recipients is None:
        abort

    headers = {
        'Access-Control-Allow-Origin': HOSTS,
        'Access-Control-Allow-Methods': 'POST'
    }
    if isinstance(recipients, list):
        msg = messaging.MulticastMessage(
            notification=messaging.Notification(
                title="ands notification", body=message),
            tokens=recipients)
        resp = messaging.send_multicast(msg, app=DEFAULT_APP)
        return (f'{resp.success_count} successfully sent, {resp.failure_count} failed', 200, headers)
    else:
        msg = messaging.Message(
            notification=messaging.Notification(
                title="ands message", body=message),
            token=recipients)
        resp = messaging.send(msg, app=DEFAULT_APP)
        return (f'{resp} sent', 200, headers)


# gcloud functions deploy send --project=andsnews --region=europe-west3 --runtime=python38 --trigger-http --allow-unauthenticated
