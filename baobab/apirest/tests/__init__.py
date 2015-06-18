# -*- coding: utf-8 -*-

"""
django only look for test in app_name.tests.py or app_name.tests/__init__.py
add the tests classes here to make them visible to django
"""

from .route import TestRoute
from .status import TestStatus
from .services import TestServices
from .events import TestEvents
from .utc_date import TestUTCDate
from .schema import TestSchema
