import time
import json
import base64
import logging
import httplib2
from google.appengine.api import app_identity
# from oauth2client.client import GoogleCredentials
from oauth2client.service_account import ServiceAccountCredentials
from config import FIREBASE, FB_SERVICE_ACCOUNT

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']

_IDENTITY_ENDPOINT = ('https://identitytoolkit.googleapis.com/'
                      'google.identity.identitytoolkit.v1.IdentityToolkit')


class Firebase(object):
    """
    fb = Firebase('channels')
    fb.post(path='Photo_date', payload='2016: 10')
    """
    def __init__(self, path=None):
        self.url = FIREBASE['databaseURL']
        if path:
            self.url += '/' + path

    def post(self, **kwargs):
        return self._request('POST', **kwargs)

    def _get_http(self):
        http = httplib2.Http()
        creds = ServiceAccountCredentials.from_json_keyfile_dict(FB_SERVICE_ACCOUNT, scopes=_FIREBASE_SCOPES)
        creds.authorize(http)
        return http

    def _request(self, method, **kwargs):
        url = self.url
        if 'path' in kwargs:
            url += '/' + kwargs['path']
        if 'payload' in kwargs:
            kwargs['payload'] = json.dumps(kwargs['payload'])

        response, content = self._get_http().request('%s.json' % url, method=method, body=kwargs['payload'])
        # logging.error(response)
        # logging.error(content)
        return json.loads(content)


def _get_http():
    """Provides an authed http object."""
    http = httplib2.Http()
    # Use application default credentials to make the Firebase calls
    # https://firebase.google.com/docs/reference/rest/database/user-auth
    # creds = GoogleCredentials.get_application_default().create_scoped(_FIREBASE_SCOPES)
    # creds.authorize(http)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(FB_SERVICE_ACCOUNT, scopes=_FIREBASE_SCOPES)
    creds.authorize(http)
    return http


def firebase_put(u_id, message=None):
    url = '{}/channels/{}.json'.format(FIREBASE['databaseURL'], u_id)
    response, content = _get_http().request(url, method='PUT', body=message)
    return json.loads(content)


def firebase_post(u_id, message=None):
    url = '{}/channels/{}.json'.format(FIREBASE['databaseURL'], u_id)
    response, content = _get_http().request(url, method='POST', body=message)
    return json.loads(content)


def send_firebase_message(u_id, message=None):
    """Updates data in firebase. If a message is provided, then it updates
     the data at /channels/<channel_id> with the message using the PATCH
     http method. If no message is provided, then the data at this location
     is deleted using the DELETE http method
     """
    url = '{}/channels/{}.json'.format(FIREBASE['databaseURL'], u_id)
    logging.error(u_id)
    logging.error(message)

    if message:
        return _get_http().request(url, 'PATCH', body=message)
    else:
        return _get_http().request(url, 'DELETE')


def create_custom_token(uid, valid_minutes=60):
    """Create a secure token for the given id.
    This method is used to create secure custom JWT tokens to be passed to
    clients. It takes a unique id (uid) that will be used by Firebase's
    security rules to prevent unauthorized access. In this case, the uid will
    be the channel id which is a combination of user_id and game_key
    """

    # use the app_identity service from google.appengine.api to get the
    # project's service account email automatically
    client_email = app_identity.get_service_account_name()

    now = int(time.time())
    # encode the required claims
    # per https://firebase.google.com/docs/auth/server/create-custom-tokens
    payload = base64.b64encode(json.dumps({
        'iss': client_email,
        'sub': client_email,
        'aud': _IDENTITY_ENDPOINT,
        'uid': uid,  # the important parameter, as it will be the channel id
        'iat': now,
        'exp': now + (valid_minutes * 60),
    }))
    # add standard header to identify this as a JWT
    header = base64.b64encode(json.dumps({'typ': 'JWT', 'alg': 'RS256'}))
    to_sign = '{}.{}'.format(header, payload)
    # Sign the jwt using the built in app_identity service
    return '{}.{}'.format(to_sign, base64.b64encode(
        app_identity.sign_blob(to_sign)[1]))