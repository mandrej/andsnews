import logging
from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError
from django.core.exceptions import PermissionDenied
from lib.comm import render

ERRORS = (
    (PermissionDenied, '403.html', 'FORBIDDEN', 403),
    (CapabilityDisabledError, '503.html', 'Google App Engine system maintenance', 503),
)

class GoogleAppEngineErrorMiddleware(object):
    """ Display a default template on internal google app engine errors
        http://gitorious.org/google-app-engine-django-errors/google-app-engine-django-errors/blobs/master/src/errors/middleware.py
    """
    def process_exception(self, request, exception):
        for e_type, tmpl, message, status in ERRORS:
            if isinstance(exception, e_type):
                logging.exception("Exception in request")
                return render(request, tmpl, {'message': message}, status=status)
        return None
