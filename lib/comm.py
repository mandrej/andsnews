from __future__ import division
import webapp2
import re, math
import datetime, time
import  hashlib, threading
import itertools, collections

from functools import wraps
from google.appengine.api import images, users, taskqueue, memcache, search
from google.appengine.ext import ndb, deferred
from google.appengine.runtime import apiproxy_errors
#from django.http import  Http404
#from django.shortcuts import redirect, render
#from django.conf import settings
from common import median, range_names

def make_thumbnail(kind, slug, size, mime='image/jpeg'):
    if kind == 'Photo':
        if size == 'small': _width = 240
        obj = ndb.Key('Photo', slug, 'Picture', slug).get()
    elif kind == 'Entry':
        if size == 'small': _width = 60
        m = re.match(r'(.+)_\d', slug)
        obj = ndb.Key('Entry', m.group(1), 'Img', slug).get()
        mime = obj.mime
    
    if obj is None:
        webapp2.abort(404)
    buff = obj.blob
    if size == 'normal': return buff, mime
    if size == 'small' and obj.small is not None: return obj.small, mime
    img = images.Image(buff)

    aspect = img.width/img.height
    if aspect < 1:
        aspect = 1/aspect
    _thumb = int(math.ceil(_width*aspect))

    if _thumb < img.width or _thumb < img.height:
        if size == 'small':
            img.resize(_thumb, _thumb)
        else:
            img.resize(_width, _thumb)
        try:
            if mime == 'image/png':
                out = img.execute_transforms(output_encoding=images.PNG)
            else:
                out = img.execute_transforms(output_encoding=images.JPEG)
        except apiproxy_errors.OverQuotaError:
            deferred.defer(make_thumbnail, kind, slug, size)
            return None, mime
        else:
            if size== 'small' and obj.small is None:
                obj.small = out
                if kind == 'Photo':
                    obj.rgb = median(out)
                    obj.put()
                    photo = obj.key.parent().get()
                    photo.hue, photo.lum, photo.sat = range_names(obj.rgb)
                    photo.put()
                obj.put()
        return out, mime
    else:
        return buff, mime

#class Cache:
#    def __init__(self, size=100):
#        if int(size) < 1:
#            raise AttributeError('size < 1 or not a number')
#        self.size = size
#        self.dict = collections.OrderedDict()
#        self.lock = threading.Lock()
#
#    def __getitem__(self, key):
#        with self.lock:
#            return self.dict[key]
#
#    def __setitem__(self, key, value):
#        with self.lock:
#            while len(self.dict) >= self.size:
#                self.dict.popitem(last=False)
#            self.dict[key]=value
#
#    def __delitem__(self, key):
#        with self.lock:
#            del self.dict[key]

#search_cache = Cache(size=10)

#FORBIDDEN = ('admin', '403', 'addcomment')
#def sign_helper(request):
#    referer = request.META.get('HTTP_REFERER', '/')
#    if referer.endswith(FORBIDDEN):
#        referer = '/'
#    if users.get_current_user():
#        dest_url = users.create_logout_url(referer)
#    else:
#        dest_url = users.create_login_url(referer)
#    return redirect(dest_url)
#
#def login_required(viewfunc):
#    @wraps(viewfunc)
#    def _checklogin(request, *args, **kwargs):
#        if users.get_current_user():
#            return viewfunc(request, *args, **kwargs)
#        return redirect(users.create_login_url(request.path))
#    return _checklogin
#
#def admin_required(viewfunc):
#    @wraps(viewfunc)
#    def _checklogin(request, *args, **kwargs):
#        if users.is_current_user_admin():
#            return viewfunc(request, *args, **kwargs)
#        return redirect(users.create_login_url(request.path))
#    return _checklogin
#
#def error403(request, tmpl='403.html'):
#    return render(request, tmpl, status=404)
#
#def error404(request, tmpl='404.html'):
#    path = request.path
#    qs = request.META.get('QUERY_STRING', None)
#    if qs:
#        path += '?%s' % qs
#    return render(request, tmpl, {'request_path': path}, status=404)
#
#def error500(request, tmpl='500.html'):
#    if not settings.DEVEL:
#        exclude = re.compile('bot', re.IGNORECASE)
#        ua = request.META['HTTP_USER_AGENT']
#        remote = request.META.get('REMOTE_HOST', '')
#        if not re.findall(exclude, ua):
#            stamp = time.strftime('%I:%M %p on %A', datetime.datetime.now().timetuple())
#            message = "%s\n%s\n%s" % (stamp, request.path, remote)
#            taskqueue.Task(url='/send', countdown=60, params={'msg': message}).add(queue_name='errors')
#
#    return render(request, tmpl, status=500)
