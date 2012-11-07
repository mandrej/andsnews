from google.appengine.api import users
from django.conf import settings

def auth(request):
    return {'user': users.get_current_user(),
            'is_admin': users.is_current_user_admin(),
            'devel': settings.DEVEL}
