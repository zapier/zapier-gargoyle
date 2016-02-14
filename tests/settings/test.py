"""
Used for the test suite run.
"""
from copy import deepcopy

from .base import *  # noqa

DEBUG = False

DATABASES = deepcopy(DATABASES)
del DATABASES['default']['NAME']


TEMPLATES = deepcopy(TEMPLATES)
TEMPLATES[0]['OPTIONS']['debug'] = False
