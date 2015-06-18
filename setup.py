#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import re
from setuptools import setup, find_packages

name = 'baobab'

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()
CHANGES = open(os.path.join(here, 'CHANGELOG')).read()

with open(os.path.join(here, name, '__init__.py')) as v_file:
    version = re.compile(r".*__version__ = '(.*?)'",
                         re.S).match(v_file.read()).group(1)

# django-tastypie < 0.10.0 if django < 1.5
# Django 1.6:
#   - the way to do test has changed and might not be compatible
#   - BooleanField no longer default to False:
#     - need to add explicit default value in the models
#     - or always set a value for all the fields
# Django 1.7: South is already integrated
# WARNING: the db has to handle the COALESCE function
requires = ['Django<1.6',
            'South<=0.8.4',
            'django-tastypie<0.10.0',
            'pytz',
            'oauth2',
            'markdown',
            ]

setup(
    name=name,
    version=version,
    description="Gandi's status web site",
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: Unix',
        'Programming Language :: Python :: 2.7',
        'Framework :: Django :: 1.4',
        'Framework :: Django :: 1.5',
    ],
    author='Gandi',
    author_email='feedback@gandi.net',
    url='http://gandi.net/',
    license='GPL-3',
    include_package_data=True,
    install_requires=requires,
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'baobab = baobab.bin.cmd_baobab:main',
        ],
    }
)
