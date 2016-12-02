import json
import logging
import httplib2
from oauth2client.service_account import ServiceAccountCredentials
from config import FIREBASE, FB_SERVICE_ACCOUNT

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

        # logging.error('%s %s' % (method, url))
        response, content = self._get_http().request('%s?print=pretty' % url, method=method, body=kwargs['payload'])
        # logging.error(response.status)
        return json.loads(content)
