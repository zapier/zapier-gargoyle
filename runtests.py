#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import os
import sys

import pytest


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.test')
    sys.path.insert(0, 'tests')
    return pytest.main()


if __name__ == '__main__':
    sys.exit(main())
