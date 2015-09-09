from django.contrib.auth.models import User
from django.http import HttpRequest
from django.template import Context, Template, TemplateSyntaxError
from django.test import TestCase

from gargoyle.builtins import UserConditionSet
from gargoyle.manager import SwitchManager
from gargoyle.models import DISABLED, GLOBAL, SELECTIVE, Switch


class TemplateTagTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='foo', email='foo@example.com')
        self.gargoyle = SwitchManager(Switch, key='key', value='value', instances=True)
        self.gargoyle.register(UserConditionSet(User))

    def test_simple(self):
        Switch.objects.create(
            key='test',
            status=GLOBAL,
        )

        template = Template("""
            {% load gargoyle_tags %}
            {% ifswitch test %}
            hello world!
            {% endifswitch %}
        """)
        rendered = template.render(Context())

        self.assertTrue('hello world!' in rendered)

    def test_else(self):
        Switch.objects.create(
            key='test',
            status=DISABLED,
        )

        template = Template("""
            {% load gargoyle_tags %}
            {% ifswitch test %}
            hello world!
            {% else %}
            foo bar baz
            {% endifswitch %}
        """)
        rendered = template.render(Context())

        self.assertTrue('foo bar baz' in rendered)
        self.assertFalse('hello world!' in rendered)

    def test_with_request(self):
        condition_set = 'gargoyle.builtins.UserConditionSet(auth.user)'

        switch = Switch.objects.create(
            key='test',
            status=SELECTIVE,
        )
        switch = self.gargoyle['test']

        switch.add_condition(
            condition_set=condition_set,
            field_name='percent',
            condition='0-50',
        )

        request = HttpRequest()
        request.user = self.user

        template = Template("""
            {% load gargoyle_tags %}
            {% ifswitch test %}
            hello world!
            {% else %}
            foo bar baz
            {% endifswitch %}
        """)
        rendered = template.render(Context({'request': request}))

        self.assertFalse('foo bar baz' in rendered)
        self.assertTrue('hello world!' in rendered)

    def test_missing_name(self):
        self.assertRaises(TemplateSyntaxError, Template, """
            {% load gargoyle_tags %}
            {% ifswitch %}
            hello world!
            {% endifswitch %}
        """)

    def test_with_custom_objects(self):
        condition_set = 'gargoyle.builtins.UserConditionSet(auth.user)'

        switch = Switch.objects.create(
            key='test',
            status=SELECTIVE,
        )
        switch = self.gargoyle['test']

        switch.add_condition(
            condition_set=condition_set,
            field_name='percent',
            condition='0-50',
        )

        request = HttpRequest()
        request.user = self.user

        # Pass in request.user explicitly.
        template = Template("""
            {% load gargoyle_tags %}
            {% ifswitch test request.user %}
            hello world!
            {% else %}
            foo bar baz
            {% endifswitch %}
        """)
        rendered = template.render(Context({'request': request}))

        self.assertFalse('foo bar baz' in rendered)
        self.assertTrue('hello world!' in rendered)
