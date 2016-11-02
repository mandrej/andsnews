import time
import json
import jwt
import base64
import logging
import httplib2
import Crypto.PublicKey.RSA as RSA
from google.appengine.api import app_identity
from oauth2client.client import GoogleCredentials
from config import FIREBASE, SERVICE_ACCOUNT

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']

_IDENTITY_ENDPOINT = ('https://identitytoolkit.googleapis.com/'
                      'google.identity.identitytoolkit.v1.IdentityToolkit')


def _get_http():
    """Provides an authed http object."""
    http = httplib2.Http()
    # Use application default credentials to make the Firebase calls
    # https://firebase.google.com/docs/reference/rest/database/user-auth
    creds = GoogleCredentials.get_application_default().create_scoped(_FIREBASE_SCOPES)
    creds.authorize(http)
    return http


def send_firebase_message(u_id, message=None):
    """Updates data in firebase. If a message is provided, then it updates
     the data at /channels/<channel_id> with the message using the PATCH
     http method. If no message is provided, then the data at this location
     is deleted using the DELETE http method
     """
    url = '{}/channels/{}.json'.format(FIREBASE['databaseURL'], u_id)
    logging.error(u_id)
    logging.error(message)
    logging.error(url)

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
    # client_email = app_identity.get_service_account_name()
    private_key = RSA.importKey("-----BEGIN PRIVATE KEY-----\n...")

    now = int(time.time())
    exp = now + (valid_minutes * 60)
    # encode the required claims
    # per https://firebase.google.com/docs/auth/server/create-custom-tokens
    payload = {
        'iss': SERVICE_ACCOUNT,
        'sub': SERVICE_ACCOUNT,
        'aud': _IDENTITY_ENDPOINT,
        'uid': uid,  # the important parameter, as it will be the channel id
        'iat': now,
    }
    logging.error(jwt.generate_jwt(payload, private_key, "RS256", exp))
    return jwt.generate_jwt(payload, private_key, "RS256", exp)
    # add standard header to identify this as a JWT
    # header = base64.b64encode(json.dumps({'typ': 'JWT', 'alg': 'RS256'}))
    # to_sign = '{}.{}'.format(header, payload)
    # # Sign the jwt using the built in app_identity service
    # return '{}.{}'.format(to_sign, base64.b64encode(
    #     app_identity.sign_blob(to_sign)[1]))
