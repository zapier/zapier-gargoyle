from django.test import TestCase

from gargoyle.conditions import ConditionSet, Range
from gargoyle.manager import SwitchManager
from gargoyle.models import SELECTIVE, Switch


class NumberConditionSet(ConditionSet):
    in_range = Range()

    def get_field_value(self, instance, field_name):
        if field_name == 'in_range':
            return instance


class NumberConditionSetTests(TestCase):

    condition_set = __name__ + '.' + NumberConditionSet.__name__

    def setUp(self):
        super(NumberConditionSetTests, self).setUp()
        self.gargoyle = SwitchManager(Switch, key='key', value='value', instances=True, auto_create=True)
        self.gargoyle.register(NumberConditionSet())

        Switch.objects.create(key='test', status=SELECTIVE)
        self.switch = self.gargoyle['test']

    def test_range(self):
        self.switch.add_condition(
            condition_set=self.condition_set,
            field_name='in_range',
            condition='1-3',
        )

        assert not self.gargoyle.is_active('test', 0)
        assert self.gargoyle.is_active('test', 1)
        assert self.gargoyle.is_active('test', 2)
        assert self.gargoyle.is_active('test', 3)
        assert not self.gargoyle.is_active('test', 4)
