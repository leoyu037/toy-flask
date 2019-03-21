#!/usr/bin/env python

from setuptools import setup

setup(
    name='toy-flask',
    version='1.0',
    requires=['flask'],
    install_requires=[
        'flask',
        'ddtrace',
        'pytest',
    ],
)
