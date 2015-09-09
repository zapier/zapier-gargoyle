import socket

from django.test import TestCase

from gargoyle.builtins import HostConditionSet
from gargoyle.manager import SwitchManager
from gargoyle.models import SELECTIVE, Switch


class HostConditionSetTest(TestCase):
    def setUp(self):
        self.gargoyle = SwitchManager(Switch, key='key', value='value', instances=True, auto_create=True)
        self.gargoyle.register(HostConditionSet())

    def test_simple(self):
        condition_set = 'gargoyle.builtins.HostConditionSet'

        # we need a better API for this (model dict isnt cutting it)
        switch = Switch.objects.create(
            key='test',
            status=SELECTIVE,
        )
        switch = self.gargoyle['test']

        self.assertFalse(self.gargoyle.is_active('test'))

        switch.add_condition(
            condition_set=condition_set,
            field_name='hostname',
            condition=socket.gethostname(),
        )

        self.assertTrue(self.gargoyle.is_active('test'))
