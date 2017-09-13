"""
gargoyle.nexus_modules
~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2010 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""
from __future__ import absolute_import, division, print_function, unicode_literals

import logging
from functools import wraps

import nexus
from django.conf import settings
from django.conf.urls import url
from django.http import HttpResponse, HttpResponseNotFound
from django.utils import six

from gargoyle import gargoyle, signals
from gargoyle.conditions import ValidationError
from gargoyle.helpers import dumps
from gargoyle.models import DISABLED, Switch

logger = logging.getLogger('gargoyle.switches')


class GargoyleException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


def json_view(func):
    "Decorator to make JSON views simpler"

    @wraps(func)
    def wrapper(self, request, *args, **kwargs):
        try:
            response = {
                "success": True,
                "data": func(self, request, *args, **kwargs)
            }
        except GargoyleException as exc:
            response = {
                "success": False,
                "data": exc.message
            }
        except Switch.DoesNotExist:
            response = {
                "success": False,
                "data": "Switch cannot be found"
            }
        except ValidationError as e:
            response = {
                "success": False,
                "data": u','.join(map(six.text_type, e.messages)),
            }
        except Exception:
            if settings.DEBUG:
                import traceback
                traceback.print_exc()
            raise
        return HttpResponse(dumps(response), content_type="application/json")

    return wrapper


class GargoyleModule(nexus.NexusModule):
    home_url = 'index'
    name = 'gargoyle'

    def get_title(self):
        return 'Gargoyle'

    def get_urls(self):
        return [
            url(r'^add/$', self.as_view(self.add), name='add'),
            url(r'^update/$', self.as_view(self.update), name='update'),
            url(r'^delete/$', self.as_view(self.delete), name='delete'),
            url(r'^status/$', self.as_view(self.status), name='status'),
            url(r'^conditions/add/$', self.as_view(self.add_condition), name='add-condition'),
            url(r'^conditions/remove/$', self.as_view(self.remove_condition), name='remove-condition'),
            url(r'^$', self.as_view(self.index), name='index'),
        ]

    def render_on_dashboard(self, request):
        active_switches_count = Switch.objects.exclude(status=DISABLED).count()

        switches = list(Switch.objects.exclude(status=DISABLED).order_by("date_created")[:5])

        return self.render_to_string('gargoyle/nexus/dashboard.html', {
            'switches': switches,
            'active_switches_count': active_switches_count,
        })

    def index(self, request):
        sort_by = request.GET.get('by', '-date_modified')

        if sort_by not in self.valid_sort_orders:
            return HttpResponseNotFound('Invalid sort order.')

        switches = list(Switch.objects.all().order_by(sort_by))

        return self.render_to_response("gargoyle/index.html", {
            "switches": [s.to_dict(gargoyle) for s in switches],
            "all_conditions": list(gargoyle.get_all_conditions()),
            "sorted_by": sort_by
        }, request)

    @json_view
    def add(self, request):
        key = request.POST.get("key")

        if not key:
            raise GargoyleException("Key cannot be empty")

        if len(key) > 64:
            raise GargoyleException("Key must be less than or equal to 64 characters in length")

        label = request.POST.get("name", "").strip()

        if len(label) > 64:
            raise GargoyleException("Name must be less than or equal to 64 characters in length")

        switch, created = Switch.objects.get_or_create(
            key=key,
            defaults=dict(
                label=label or None,
                description=request.POST.get("desc")
            )
        )

        if not created:
            raise GargoyleException("Switch with key %s already exists" % key)

        logger.info('Switch %r added (%%s)' % switch.key,
                    ', '.join('%s=%r' % (k, getattr(switch, k)) for k in sorted(('key', 'label', 'description', ))))

        signals.switch_added.send(
            sender=self,
            request=request,
            switch=switch,
        )

        return switch.to_dict(gargoyle)

    @json_view
    def update(self, request):
        switch = Switch.objects.get(key=request.POST.get("curkey"))

        key = request.POST.get("key")

        if len(key) > 64:
            raise GargoyleException("Key must be less than or equal to 64 characters in length")

        label = request.POST.get("name", "")

        if len(label) > 64:
            raise GargoyleException("Name must be less than or equal to 64 characters in length")

        values = dict(
            label=label,
            key=key,
            description=request.POST.get("desc"),
        )

        changes = {}
        for attribute, value in six.iteritems(values):
            new_value = getattr(switch, attribute)
            if new_value != value:
                changes[attribute] = (value, new_value)

        if changes:
            if switch.key != key:
                switch.delete()
                switch.key = key

            switch.label = label
            switch.description = request.POST.get("desc")
            switch.save()

            logger.info('Switch %r updated %%s' % switch.key,
                        ', '.join('%s=%r->%r' % (k, v[0], v[1]) for k, v in sorted(six.iteritems(changes))))

            signals.switch_updated.send(
                sender=self,
                request=request,
                switch=switch,
                changes=changes,
            )

        return switch.to_dict(gargoyle)

    @json_view
    def status(self, request):
        switch = Switch.objects.get(key=request.POST.get("key"))

        try:
            status = int(request.POST.get("status"))
        except ValueError:
            raise GargoyleException("Status must be integer")

        old_status = switch.status
        old_status_label = switch.get_status_display()

        if switch.status != status:
            switch.status = status
            switch.save()

            logger.info('Switch %r updated (status=%%s->%%s)' % switch.key,
                        old_status_label, switch.get_status_display())

            signals.switch_status_updated.send(
                sender=self,
                request=request,
                switch=switch,
                old_status=old_status,
                status=status,
            )

        return switch.to_dict(gargoyle)

    @json_view
    def delete(self, request):
        switch = Switch.objects.get(key=request.POST.get("key"))
        switch.delete()

        logger.info('Switch %r removed' % switch.key)

        signals.switch_deleted.send(
            sender=self,
            request=request,
            switch=switch,
        )

        return {}

    @json_view
    def add_condition(self, request):
        key = request.POST.get("key")
        condition_set_id = request.POST.get("id")
        field_name = request.POST.get("field")
        exclude = int(request.POST.get("exclude") or 0)

        if not all([key, condition_set_id, field_name]):
            raise GargoyleException("Fields cannot be empty")

        field = gargoyle.get_condition_set_by_id(condition_set_id).fields[field_name]
        value = field.validate(request.POST)

        switch = gargoyle[key]
        switch.add_condition(condition_set_id, field_name, value, exclude=exclude)

        logger.info('Condition added to %r (%r, %s=%r, exclude=%r)' % (switch.key,
                    condition_set_id, field_name, value, bool(exclude)))

        signals.switch_condition_added.send(
            sender=self,
            request=request,
            switch=switch,
            condition={
                'condition_set_id': condition_set_id,
                'field_name': field_name,
                'value': value,
            },
        )

        return switch.to_dict(gargoyle)

    @json_view
    def remove_condition(self, request):
        key = request.POST.get("key")
        condition_set_id = request.POST.get("id")
        field_name = request.POST.get("field")
        value = request.POST.get("value")

        if not all([key, condition_set_id, field_name]):
            raise GargoyleException("Fields cannot be empty")

        switch = gargoyle[key]
        switch.remove_condition(condition_set_id, field_name, value)

        logger.info('Condition removed from %r (%r, %s=%r)' % (switch.key,
                    condition_set_id, field_name, value))

        signals.switch_condition_removed.send(
            sender=self,
            request=request,
            switch=switch,
            condition={
                'condition_set_id': condition_set_id,
                'field_name': field_name,
                'value': value,
            },
        )

        return switch.to_dict(gargoyle)

    @property
    def valid_sort_orders(self):
        fields = ['label', 'date_created', 'date_modified']
        return fields + ['-' + f for f in fields]


nexus.site.register(GargoyleModule, 'gargoyle')
