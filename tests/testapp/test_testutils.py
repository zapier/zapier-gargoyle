from django.test import TestCase

from gargoyle.manager import SwitchManager
from gargoyle.models import DISABLED, GLOBAL, Switch
from gargoyle.testutils import switches


class SwitchContextManagerTest(TestCase):
    def setUp(self):
        self.gargoyle = SwitchManager(Switch, key='key', value='value', instances=True, auto_create=True)

    def test_as_decorator(self):
        switch = self.gargoyle['test']
        switch.status = DISABLED

        @switches(self.gargoyle, test=True)
        def test():
            return self.gargoyle.is_active('test')

        self.assertTrue(test())
        self.assertEquals(self.gargoyle['test'].status, DISABLED)

        switch.status = GLOBAL
        switch.save()

        @switches(self.gargoyle, test=False)
        def test2():
            return self.gargoyle.is_active('test')

        self.assertFalse(test2())
        self.assertEquals(self.gargoyle['test'].status, GLOBAL)

    def test_context_manager(self):
        switch = self.gargoyle['test']
        switch.status = DISABLED

        with switches(self.gargoyle, test=True):
            self.assertTrue(self.gargoyle.is_active('test'))

        self.assertEquals(self.gargoyle['test'].status, DISABLED)

        switch.status = GLOBAL
        switch.save()

        with switches(self.gargoyle, test=False):
            self.assertFalse(self.gargoyle.is_active('test'))

        self.assertEquals(self.gargoyle['test'].status, GLOBAL)
