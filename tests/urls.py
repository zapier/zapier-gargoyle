"""
:copyright: (c) 2010 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""
import nexus

try:
    # Django <1.6
    from django.conf.urls.defaults import include, patterns, url
except ImportError:
    # Django >=1.6
    from django.conf.urls import include, patterns, url


def foo(request):
    from django.http import HttpResponse
    return HttpResponse()

nexus.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^nexus/', include(nexus.site.urls)),
    url(r'^$', foo, name='gargoyle_test_foo'),
)
