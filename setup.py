#!/usr/bin/env python
from setuptools import setup, find_packages

install_requires = [
    'django-modeldict>=1.2.0',
    'nexus>=0.2.3',
    'django-jsonfield>=0.9.2,!=0.9.13',
]


setup(
    name='gargoyle-yplan',
    version='1.0.0',
    author='DISQUS',
    author_email='opensource@disqus.com',
    maintainer='YPlan',
    maintainer_email='adam@yplanapp.com',
    url='https://github.com/yplan/gargoyle',
    description='Gargoyle is a platform built on top of Django which allows you to switch functionality of your application on and off based on conditions.',
    packages=find_packages(exclude=["example_project", "tests"]),
    zip_safe=False,
    install_requires=install_requires,
    license='Apache License 2.0',
    include_package_data=True,
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Software Development'
    ],
)
