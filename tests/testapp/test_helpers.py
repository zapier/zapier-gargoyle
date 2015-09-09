from django.contrib.auth.models import AnonymousUser, User
from django.test import TestCase

from gargoyle.helpers import MockRequest
from gargoyle.manager import SwitchManager
from gargoyle.models import Switch


class MockRequestTest(TestCase):
    def setUp(self):
        self.gargoyle = SwitchManager(Switch, key='key', value='value', instances=True)

    def test_empty_attrs(self):
        req = MockRequest()
        self.assertEquals(req.META['REMOTE_ADDR'], None)
        self.assertEquals(req.user.__class__, AnonymousUser)

    def test_ip(self):
        req = MockRequest(ip_address='127.0.0.1')
        self.assertEquals(req.META['REMOTE_ADDR'], '127.0.0.1')
        self.assertEquals(req.user.__class__, AnonymousUser)

    def test_user(self):
        user = User.objects.create(username='foo', email='foo@example.com')
        req = MockRequest(user=user)
        self.assertEquals(req.META['REMOTE_ADDR'], None)
        self.assertEquals(req.user, user)

    def test_as_request(self):
        user = User.objects.create(username='foo', email='foo@example.com')

        req = self.gargoyle.as_request(user=user, ip_address='127.0.0.1')

        self.assertEquals(req.META['REMOTE_ADDR'], '127.0.0.1')
        self.assertEquals(req.user, user)
