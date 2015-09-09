from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from gargoyle.management.commands.add_switch import Command as AddSwitchCmd
from gargoyle.management.commands.remove_switch import Command as RemoveSwitchCmd
from gargoyle.manager import SwitchManager
from gargoyle.models import DISABLED, GLOBAL, Switch


class CommandAddSwitchTestCase(TestCase):

    def setUp(self):
        self.gargoyle = SwitchManager(Switch, key='key', value='value', instances=True, auto_create=True)

    def test_requires_single_arg(self):
        too_few_too_many = [
            [],
            ['one', 'two'],
        ]
        for args in too_few_too_many:
            command = AddSwitchCmd()

            self.assertRaises(CommandError, command.handle, *args)

    def test_add_switch_default_status(self):
        self.assertFalse('switch_default' in self.gargoyle)

        call_command('add_switch', 'switch_default')

        self.assertTrue('switch_default' in self.gargoyle)
        self.assertEqual(GLOBAL, self.gargoyle['switch_default'].status)

    def test_add_switch_with_status(self):
        self.assertFalse('switch_disabled' in self.gargoyle)

        call_command('add_switch', 'switch_disabled', status=DISABLED)

        self.assertTrue('switch_disabled' in self.gargoyle)
        self.assertEqual(DISABLED, self.gargoyle['switch_disabled'].status)

    def test_update_switch_status_disabled(self):
        Switch.objects.create(key='test', status=GLOBAL)
        self.assertEqual(GLOBAL, self.gargoyle['test'].status)

        call_command('add_switch', 'test', status=DISABLED)

        self.assertEqual(DISABLED, self.gargoyle['test'].status)

    def test_update_switch_status_to_default(self):
        Switch.objects.create(key='test', status=DISABLED)
        self.assertEqual(DISABLED, self.gargoyle['test'].status)

        call_command('add_switch', 'test')

        self.assertEqual(GLOBAL, self.gargoyle['test'].status)


class CommandRemoveSwitchTestCase(TestCase):

    def setUp(self):
        self.gargoyle = SwitchManager(Switch, key='key', value='value', instances=True, auto_create=True)

    def test_requires_single_arg(self):
        too_few_too_many = [
            [],
            ['one', 'two'],
        ]
        for args in too_few_too_many:
            command = RemoveSwitchCmd()

            self.assertRaises(CommandError, command.handle, *args)

    def test_removes_switch(self):
        Switch.objects.create(key='test')
        self.assertTrue('test' in self.gargoyle)

        call_command('remove_switch', 'test')

        self.assertFalse('test' in self.gargoyle)

    def test_remove_non_switch_doesnt_error(self):
        self.assertFalse('idontexist' in self.gargoyle)

        call_command('remove_switch', 'idontexist')

        self.assertFalse('idontexist' in self.gargoyle)
