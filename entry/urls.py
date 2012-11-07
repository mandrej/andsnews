from django.conf.urls.defaults import patterns, url
from views import index, thumb, add, edit, delete, detail

urlpatterns = patterns('',
    url(r'^(?P<field>tags|date|author)/(?P<value>.+)$', index),
    url(r'^image/(?P<slug>[-\w]+)/(?P<size>small|normal)$', thumb),
    url(r'^add$', add),
    url(r'^(?P<slug>[-\w]+)/edit$', edit),
    url(r'^(?P<slug>[-\w]+)/delete$', delete),
    url(r'^(?P<slug>[-\w]+)$', detail),
    url(r'^$', index),
)
