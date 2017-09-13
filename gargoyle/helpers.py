"""
gargoyle.helpers
~~~~~~~~~~~~~~~~

:copyright: (c) 2010 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""
from __future__ import absolute_import, division, print_function, unicode_literals

import datetime
import json
import uuid

from django.core.serializers.json import DjangoJSONEncoder


class BetterJSONEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            return obj.hex
        elif isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        elif isinstance(obj, (set, frozenset)):
            return list(obj)
        return super(BetterJSONEncoder, self).default(obj)


def dumps(value, **kwargs):
    return json.dumps(value, cls=BetterJSONEncoder, **kwargs)
