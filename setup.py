#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='toy-flask',
    version='1.0',
    packages=find_packages(exclude=['test']),
    install_requires=[
        'flask',
        'ddtrace',
        'pytest',
    ],
)
