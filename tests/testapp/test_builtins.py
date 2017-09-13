from __future__ import absolute_import, division, print_function, unicode_literals

import datetime
import socket

import pytz
from django.test import RequestFactory, TestCase
from django.test.utils import override_settings
from django.utils import timezone
from freezegun import freeze_time

from gargoyle.builtins import (
    ActiveTimezoneTodayConditionSet, AppTodayConditionSet, HostConditionSet, IPAddressConditionSet,
    UTCTodayConditionSet
)
from gargoyle.manager import SwitchManager
from gargoyle.models import SELECTIVE, Switch


class IPAddressConditionSetTests(TestCase):

    condition_set = 'gargoyle.builtins.IPAddressConditionSet'

    def setUp(self):
        super(IPAddressConditionSetTests, self).setUp()
        self.gargoyle = SwitchManager(Switch, key='key', value='value', instances=True, auto_create=True)
        self.gargoyle.register(IPAddressConditionSet())
        self.request_factory = RequestFactory()

        Switch.objects.create(key='test', status=SELECTIVE)
        self.switch = self.gargoyle['test']
        assert not self.gargoyle.is_active('test')

    def test_percent(self):
        self.switch.add_condition(
            condition_set=self.condition_set,
            field_name='percent',
            condition='0-100',
        )

        request = self.request_factory.get('/', REMOTE_ADDR='1.0.0.0')
        assert self.gargoyle.is_active('test', request)

    def test_0_percent(self):
        self.switch.add_condition(
            condition_set=self.condition_set,
            field_name='percent',
            condition='0-0',
        )

        request = self.request_factory.get('/', REMOTE_ADDR='1.0.0.0')
        assert not self.gargoyle.is_active('test', request)

    def test_specific_address(self):
        self.switch.add_condition(
            condition_set=self.condition_set,
            field_name='ip_address',
            condition='1.1.1.1',
        )

        request = self.request_factory.get('/', REMOTE_ADDR='1.0.0.0')
        assert not self.gargoyle.is_active('test', request)

        request = self.request_factory.get('/', REMOTE_ADDR='1.1.1.1')
        assert self.gargoyle.is_active('test', request)

    @override_settings(INTERNAL_IPS=['1.0.0.0'])
    def test_internal_ip(self):
        self.switch.add_condition(
            condition_set=self.condition_set,
            field_name='internal_ip',
            condition='',
        )

        request = self.request_factory.get('/', REMOTE_ADDR='1.0.0.0')
        assert self.gargoyle.is_active('test', request)

        request = self.request_factory.get('/', REMOTE_ADDR='1.1.1.1')
        assert not self.gargoyle.is_active('test', request)

    @override_settings(INTERNAL_IPS=['1.0.0.0'])
    def test_not_internal_ip(self):
        self.switch.add_condition(
            condition_set=self.condition_set,
            field_name='internal_ip',
            condition='',
            exclude=True,
        )

        request = self.request_factory.get('/', REMOTE_ADDR='1.0.0.0')
        assert not self.gargoyle.is_active('test', request)

        request = self.request_factory.get('/', REMOTE_ADDR='1.1.1.1')
        assert self.gargoyle.is_active('test', request)


class HostConditionSetTests(TestCase):
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

        assert not self.gargoyle.is_active('test')

        switch.add_condition(
            condition_set=condition_set,
            field_name='hostname',
            condition=socket.gethostname(),
        )

        assert self.gargoyle.is_active('test')


class UTCTodayConditionSetTests(TestCase):
    def setUp(self):
        """
        Assume we have:
        - server with `America/Chicago` timezone
        - app with `America/New_York` timezone (if Django timezone support enabled)
        - current timezone `Europe/Moscow` (if active)
        - then it is 2016-01-01T00:00:00 at server
        """
        self.condition_set = UTCTodayConditionSet()
        self.server_dt = datetime.datetime(2016, 1, 1, 0, 0, 0)
        self.server_tz = pytz.timezone('America/Chicago')
        self.server_dt_aware = self.server_tz.localize(self.server_dt)
        self.server_tz_offset = -6
        self.utc_dt = self.server_dt - datetime.timedelta(hours=self.server_tz_offset)

    @override_settings(USE_TZ=True, TIME_ZONE="America/New_York")
    @timezone.override('Europe/Moscow')
    def test_use_tz_with_active(self):
        with freeze_time(self.server_dt_aware, tz_offset=self.server_tz_offset):
            assert self.condition_set.get_field_value(None, 'now_is_on_or_after') == self.utc_dt

    @override_settings(USE_TZ=True, TIME_ZONE="America/New_York")
    @timezone.override(None)
    def test_use_tz_no_active(self):
        with freeze_time(self.server_dt_aware, tz_offset=self.server_tz_offset):
            assert self.condition_set.get_field_value(None, 'now_is_on_or_after') == self.utc_dt

    @override_settings(USE_TZ=False, TIME_ZONE=None)
    @timezone.override('Europe/Moscow')
    def test_no_use_tz_with_active(self):
        with freeze_time(self.server_dt_aware, tz_offset=self.server_tz_offset):
            assert self.condition_set.get_field_value(None, 'now_is_on_or_after') == self.utc_dt

    @override_settings(USE_TZ=False, TIME_ZONE=None)
    @timezone.override(None)
    def test_no_use_tz_without_active(self):
        with freeze_time(self.server_dt_aware, tz_offset=self.server_tz_offset):
            assert self.condition_set.get_field_value(None, 'now_is_on_or_after') == self.utc_dt


class AppTodayConditionSetTests(TestCase):
    def setUp(self):
        """
        Assume we have:
        - server with `America/Chicago` timezone
        - app with `America/New_York` timezone (if Django timezone support enabled)
        - current timezone `Europe/Moscow` (if active)
        - then it is 2016-01-01T00:00:00 at server
        """
        self.condition_set = AppTodayConditionSet()
        self.server_dt = datetime.datetime(2016, 1, 1, 0, 0, 0)
        self.server_tz = pytz.timezone('America/Chicago')
        self.server_dt_aware = self.server_tz.localize(self.server_dt)
        self.server_tz_offset = -6
        self.app_to_server_tz_offset = datetime.timedelta(hours=1)

    @override_settings(USE_TZ=True, TIME_ZONE="America/New_York")
    @timezone.override('Europe/Moscow')
    def test_use_tz_with_active(self):
        with freeze_time(self.server_dt_aware, tz_offset=self.server_tz_offset):
            assert (
                self.condition_set.get_field_value(None, 'now_is_on_or_after') ==
                self.server_dt + self.app_to_server_tz_offset
            )

    @override_settings(USE_TZ=True, TIME_ZONE="America/New_York")
    @timezone.override(None)
    def test_use_tz_no_active(self):
        with freeze_time(self.server_dt_aware, tz_offset=self.server_tz_offset):
            assert (
                self.condition_set.get_field_value(None, 'now_is_on_or_after') ==
                self.server_dt + self.app_to_server_tz_offset
            )

    @override_settings(USE_TZ=False, TIME_ZONE=None)
    @timezone.override('Europe/Moscow')
    def test_no_use_tz_with_active(self):
        with freeze_time(self.server_dt_aware, tz_offset=self.server_tz_offset):
            assert self.condition_set.get_field_value(None, 'now_is_on_or_after') == self.server_dt

    @override_settings(USE_TZ=False, TIME_ZONE=None)
    @timezone.override(None)
    def test_no_use_tz_without_active(self):
        with freeze_time(self.server_dt_aware, tz_offset=self.server_tz_offset):
            assert self.condition_set.get_field_value(None, 'now_is_on_or_after') == self.server_dt


class ActiveTimezoneTodayConditionSetTests(TestCase):
    def setUp(self):
        """
        Assume we have:
        - server with `America/Chicago` timezone
        - app with `America/New_York` timezone (if Django timezone support enabled)
        - current timezone `Europe/Moscow` (if active)
        - then it is 2016-01-01T00:00:00 at server
        """
        self.condition_set = ActiveTimezoneTodayConditionSet()
        self.server_dt = datetime.datetime(2016, 1, 1, 0, 0, 0)
        self.server_tz = pytz.timezone('America/Chicago')
        self.server_dt_aware = self.server_tz.localize(self.server_dt)
        self.server_tz_offset = -6
        self.app_to_server_tz_offset = datetime.timedelta(hours=1)
        self.active_to_server_tz_offset = datetime.timedelta(hours=9)

    @override_settings(USE_TZ=True, TIME_ZONE="America/New_York")
    @timezone.override('Europe/Moscow')
    def test_use_tz_with_active(self):
        with freeze_time(self.server_dt_aware, tz_offset=self.server_tz_offset):
            assert (
                self.condition_set.get_field_value(None, 'now_is_on_or_after') ==
                self.server_dt + self.active_to_server_tz_offset
            )

    @override_settings(USE_TZ=True, TIME_ZONE="America/New_York")
    @timezone.override(None)
    def test_use_tz_no_active(self):
        with freeze_time(self.server_dt_aware, tz_offset=self.server_tz_offset):
            assert (
                self.condition_set.get_field_value(None, 'now_is_on_or_after') ==
                self.server_dt + self.app_to_server_tz_offset
            )

    @override_settings(USE_TZ=False, TIME_ZONE=None)
    @timezone.override('Europe/Moscow')
    def test_no_use_tz_with_active(self):
        with freeze_time(self.server_dt_aware, tz_offset=self.server_tz_offset):
            assert self.condition_set.get_field_value(None, 'now_is_on_or_after') == self.server_dt

    @override_settings(USE_TZ=False, TIME_ZONE=None)
    @timezone.override(None)
    def test_no_use_tz_without_active(self):
        with freeze_time(self.server_dt_aware, tz_offset=self.server_tz_offset):
            assert self.condition_set.get_field_value(None, 'now_is_on_or_after') == self.server_dt
