# -*- coding: utf-8 -*-

"""
django only look for test in app_name.tests.py or app_name.tests/__init__.py
add the tests classes here to make them visible to django
"""

from .test_route import TestRoute
from .test_status import TestStatus
from .test_services import TestServices
from .test_events import TestEvents
from .test_utc_date import TestUTCDate
from .test_schema import TestSchema
