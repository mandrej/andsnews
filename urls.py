#if settings.DEVEL:
#    logging.getLogger().setLevel(logging.DEBUG)

#urlpatterns = patterns('',
#    url(r'^photos/?', include('photo.urls')),
#    url(r'^entries/?', include('entry.urls')),
#    url(r'^comments/?', include('comment.urls')),
#    url(r'^news/?', include('news.urls')),
    url(r'^admin/?', include('admin.urls')),
    url(r'^i18n/', include('django.conf.urls.i18n')),
    
#    url(r'^sitemap\.xml$', sitemap),
    url(r'^_ah/xmpp/message/chat/$', chat),
#    url(r'^filter/(?P<key>[\w]+)/(?P<value>.+)$', render_cloud),
#    url(r'^filter/(?P<key>[\w]+)$', render_cloud),
#    url(r'^visualize/(?P<key>[\w]+)$', visualize),
#    url(r'^rss/(?P<kind>photo|entry)\.xml$', rss),
#    url(r'^complete/(?P<kind>photo|entry|feed)/(?P<field>tags|lens)$', auto_complete),
    url(r'^search$', find),
    url(r'^send$', send),
#    url(r'^sitemap\.xml$', sitemap),
#    url(r'^latest$', latest),
    url(r'^$', index),
#)
#handler403 = 'lib.comm.error403'
#handler404 = 'lib.comm.error404'
#handler500 = 'lib.comm.error500'
