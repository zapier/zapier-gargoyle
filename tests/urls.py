"""
:copyright: (c) 2010 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""
import nexus
from django.conf.urls import include, url
from django.contrib import admin

from gargoyle.compat import subinclude


def foo(request):
    from django.http import HttpResponse
    return HttpResponse()

admin.autodiscover()
nexus.autodiscover()

urlpatterns = [
    url(r'^nexus/', include(nexus.site.urls)),
    url(r'^admin/', subinclude(admin.site.urls)),
    url(r'^$', foo, name='gargoyle_test_foo'),
]
