from flask import abort
from firebase_admin import credentials, initialize_app, messaging

cred = credentials.Certificate('credentials.json')
DEFAULT_APP = initialize_app(cred)
HOSTS = 'https://ands.appspot.com, http://localhost'


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
    message = ''
    recipients = None
    data = None

    if request_json and 'recipients' in request_json:
        recipients = request_json['recipients']
    if request_json and 'message' in request_json:
        message = request_json['message']
    if request_json and 'data' in request_json:
        data = request_json['data']

    if recipients is None:
        abort(400, description='No Recipients')

    headers = {
        'Access-Control-Allow-Origin': HOSTS,
        'Access-Control-Allow-Methods': 'POST'
    }
    payload = {"notification": messaging.Notification(
        title="ands notification", body=message)}
    if data:
        payload["data"] = data

    if isinstance(recipients, list):
        payload["tokens"] = recipients  # type: ignore
        resp = messaging.send_multicast(
            messaging.MulticastMessage(**payload), app=DEFAULT_APP)
        return (f'{resp.success_count} successfully sent, {resp.failure_count} failed', 200, headers)
    else:
        payload["token"] = recipients
        resp = messaging.send(messaging.Message(**payload), app=DEFAULT_APP)
        return (f'{resp} sent', 200, headers)


# gcloud functions deploy send --project=andsnews --region=us-central1 --runtime=python310 --trigger-http --allow-unauthenticated
