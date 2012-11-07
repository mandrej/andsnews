from django.conf.urls.defaults import patterns, url
from views import comments, comment_save, comment_delete, thumbnails, \
    thumbnail_delete, thumbnail_make, thumbnail_color, info, feeds, counters, index, \
    build, create, memcahe_content, memcache_delete

urlpatterns = patterns('',
    url(r'^comments$', comments),
    url(r'^comment/save$', comment_save),
    url(r'^comment/delete$', comment_delete),
    url(r'^photo/thumbnails/(?P<field>date|hue|lum)/(?P<value>.+)$', thumbnails, {'kind': 'Photo'}),
    url(r'^entry/thumbnails/(?P<field>date)/(?P<value>.+)$', thumbnails, {'kind': 'Entry', 'per_page': 6}),
    url(r'^photo/thumbnails$', thumbnails, {'kind': 'Photo'}),
    url(r'^entry/thumbnails$', thumbnails, {'kind': 'Entry', 'per_page': 6}),
    
    url(r'^memcache$', memcahe_content),
    url(r'^memcache/(?P<key>\w+)/build$', build),
    url(r'^memcache/(?P<key>\w+)/create$', create),
    url(r'^memcache/(?P<key>\w+)/delete$', memcache_delete),
    
    url(r'^thumbnail/delete', thumbnail_delete),
    url(r'^thumbnail/make', thumbnail_make),
    url(r'^thumbnail/color', thumbnail_color),
    url(r'^photo/info/(?P<oldkey>\w+)$', info),
    url(r'^feeds$', feeds),
    url(r'^counters$', counters),
    url(r'^$', index),
)