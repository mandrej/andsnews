from django.conf.urls.defaults import patterns, url
from views import index, delete, add, validate

urlpatterns = patterns('',
    url(r'^(?P<field>forkind|date|author)/(?P<value>.+)$', index),
    url(r'^(?P<safekey>\w+)/delete$', delete),
    url(r'^(?P<safekey>\w+)/add$', add),
    url(r'^validate$', validate),
    url(r'^$', index),
)
