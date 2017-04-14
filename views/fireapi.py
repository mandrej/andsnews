import json

import httplib2
from config import FIREBASE, FB_SERVICE_ACCOUNT
from oauth2client.service_account import ServiceAccountCredentials

_FIREBASE_SCOPES = [
    'https://www.googleapis.com/auth/firebase.database',
    'https://www.googleapis.com/auth/userinfo.email']

_IDENTITY_ENDPOINT = ('https://identitytoolkit.googleapis.com/'
                      'google.identity.identitytoolkit.v1.IdentityToolkit')


class Firebase(object):
    """
    FB = Firebase()
    FB.post(path='Photo_date.json', payload='2016: 10')
    """
    def __init__(self):
        self.url = FIREBASE['databaseURL']

    def get(self, **kwargs):
        return self._request('GET', **kwargs)

    def put(self, **kwargs):
        return self._request('PUT', **kwargs)

    def patch(self, **kwargs):
        return self._request('PATCH', **kwargs)

    def post(self, **kwargs):
        return self._request('POST', **kwargs)

    def delete(self, **kwargs):
        return self._request('DELETE', **kwargs)

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
        else:
            kwargs['payload'] = None

        # self._get_http().request('%s?print=pretty' % url, method=method, body=kwargs['payload'])
        response, content = self._get_http().request(url, method=method, body=kwargs['payload'])
        # logging.error(response.status)
        # logging.error(content)
        return json.loads(content)


def push_message(token, message=''):
    """
        Firebase Cloud Messaging Server
        content: {"multicast_id":6062741259302324809,"success":1,"failure":0,"canonical_ids":0,
            "results":[{"message_id":"0:1481827534054930%2fd9afcdf9fd7ecd"}]}
    """
    url = 'https://fcm.googleapis.com/fcm/send'
    headers = {
        'Authorization': 'key={}'.format(FIREBASE['messagingServerKey']),
        'Content-Type': 'application/json',
    }
    payload = {
        "to": token,
        "notification": {
            "title": "ands",
            "body": message
        }
    }
    http = httplib2.Http()
    response, content = http.request(url, method='POST', body=json.dumps(payload), headers=headers)
    # logging.error(response.status)
    # logging.error(content)
    # return json.loads(content)
