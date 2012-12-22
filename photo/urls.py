from django.conf.urls.defaults import patterns, url
from views import index, detail, thumb, add, edit, bind, delete

urlpatterns = patterns('',
    url(r'^(?P<field>model|iso|eqv|lens|tags|date|author|hue|lum)/(?P<value>.+)/(?P<slug>[-\w]+)$', detail),
    url(r'^(?P<field>model|iso|eqv|lens|tags|date|author|hue|lum)/(?P<value>.+)$', index),
    url(r'^(?P<slug>[-\w]+)/(?P<size>small|normal)$', thumb),
    url(r'^add$', add),
    url(r'^(?P<blob_key>.+)/bind', bind),
    url(r'^(?P<slug>[-\w]+)/edit$', edit),
    url(r'^(?P<slug>[-\w]+)/delete$', delete),
    url(r'^(?P<slug>[-\w]+)$', detail),
    url(r'^$', index),
)
