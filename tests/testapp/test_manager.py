from django.test import TestCase

from gargoyle.manager import SwitchManager
from gargoyle.models import Switch


class ConstantTest(TestCase):
    def setUp(self):
        self.gargoyle = SwitchManager(Switch, key='key', value='value', instances=True)

    def test_disabled(self):
        self.assertTrue(hasattr(self.gargoyle, 'DISABLED'))
        self.assertEquals(self.gargoyle.DISABLED, 1)

    def test_selective(self):
        self.assertTrue(hasattr(self.gargoyle, 'SELECTIVE'))
        self.assertEquals(self.gargoyle.SELECTIVE, 2)

    def test_global(self):
        self.assertTrue(hasattr(self.gargoyle, 'GLOBAL'))
        self.assertEquals(self.gargoyle.GLOBAL, 3)

    def test_include(self):
        self.assertTrue(hasattr(self.gargoyle, 'INCLUDE'))
        self.assertEquals(self.gargoyle.INCLUDE, 'i')

    def test_exclude(self):
        self.assertTrue(hasattr(self.gargoyle, 'EXCLUDE'))
        self.assertEquals(self.gargoyle.EXCLUDE, 'e')
