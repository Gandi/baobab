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

# WARNING: the db has to handle the COALESCE function
requires = ['Django>1.6',
            'django-tastypie>0.10.0',
            'pytz',
            'oauth2',
            'markdown',
            'irc<8.9.1'
            ]

extras_require = {
    'test': ['mock' ],
}

tests_requires = requires + extras_require['test']

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
    extras_require=extras_require,
    tests_require=tests_requires,
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'baobab = baobab.bin.cmd_baobab:main',
        ],
    }
)
