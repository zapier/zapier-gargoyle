import django

# Django 1.9

# url(prefix, include(urls, namespace, name)) -> url(prefix, (urls, namespace, name))
if django.VERSION[:2] >= (1, 9):
    def subinclude(urls_tuple):
        return urls_tuple  # (urls, namespace, name)
else:
    from django.conf.urls import include as subinclude  # noqa
