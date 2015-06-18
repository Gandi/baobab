# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls import patterns, include, url
from django.views.static import serve

from django.contrib import admin
admin.autodiscover()

from baobab.apirest.urls import ApiUrls as ApiRestApiUrls
from baobab.rss.feed import RssStatusFeed, AtomStatusFeed


# XXX why it's not using the middleware GZipMiddleware ????
def _serve_gzip(request):
    if not settings.SERVE_GZIP:
        return False
    if 'HTTP_ACCEPT_ENCODING' in request.META:
        encodings = request.META.get('HTTP_ACCEPT_ENCODING')
        encodings = [encoding.strip() for encoding in encodings.split(',')]
        return 'gzip' in encodings or 'deflate' in encodings
    return False


def baobab_serve(request, path, document_root=None, show_indexes=False):
    if not settings.INFINITE_CACHE:
        return serve(request, path, document_root, show_indexes)
    else:
        if _serve_gzip(request):
            resp = serve(request, path + '.gz', document_root, show_indexes)
            resp['Content-Encoding'] = 'gzip'
        else:
            resp = serve(request, path, document_root, show_indexes)
        resp['Cache-Control'] = 'public, max-age=%d' % (3600 * 24 * 365)
        resp['Vary'] = 'Accept-Encoding'
        return resp

# back-end URL
urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin', include(admin.site.urls)),
    url(r'', include(ApiRestApiUrls.get_urls())),
)

# static content URL
urlpatterns += patterns(
    '',
    url(r'^static/(?P<path>.*)$', baobab_serve,
        {'document_root': settings.MEDIA_ROOT}),
    url(r'^(favicon.ico)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT}),
)

# RSS site URL

urlpatterns += patterns(
    '',
    url(r'^rss/$', RssStatusFeed(), name='rss'),
    url(r'^atom/$', AtomStatusFeed(), name='atom'),
)

# web site URL
urlpatterns += patterns(
    '',
    url(r'^.*$', 'baobab.front.views.index'),
)
