# -*- coding: utf-8 -*-

"""
django only look for test in app_name.tests.py or app_name.tests/__init__.py
add the tests classes here to make them visible to django
"""

from .event import TestEvent
from .status import TestStatus
