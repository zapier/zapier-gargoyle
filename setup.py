#!/usr/bin/env python
import os
import re

from setuptools import setup, find_packages


def get_version(package):
    """
    Return package version as listed in `__version__` in `__init__.py`.
    """
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.search("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read().replace('.. :changelog:', '')

setup(
    name='gargoyle-yplan',
    version=get_version('gargoyle'),
    author='DISQUS',
    author_email='opensource@disqus.com',
    maintainer='YPlan',
    maintainer_email='adam@yplanapp.com',
    url='https://github.com/YPlan/gargoyle',
    description=(
        'Gargoyle is a platform built on top of Django which allows you to switch functionality of your application '
        'on and off based on conditions.'
    ),
    long_description=readme + '\n\n' + history,
    packages=find_packages(exclude=["example_project", "tests"]),
    zip_safe=False,
    install_requires=[
        'django-modeldict-yplan>=1.5.0',
        'nexus-yplan>=1.0.0',
        'django-jsonfield>=0.9.2,!=0.9.13',
    ],
    license='Apache License 2.0',
    include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python',
        'Topic :: Software Development'
    ],
)
