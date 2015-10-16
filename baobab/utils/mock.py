# -*- coding: utf-8 -*-

from baobab.socialnetwork.base import SocialNetworkBase


class MockLOG(object):

    def __init__(self):
        self._info = []
        self._error = []

    def info(self, msg, *args):
        self._info.append(msg % args)

    def error(self, msg, *args):
        self._error.append(msg % args)


class MockSN(SocialNetworkBase):
    name = 'MockSN'

    def __init__(self):
        self._msg = []

    @classmethod
    def is_configured(cls):
        True

    @classmethod
    def get_max_char(cls, default):
        return 42

    def publish(self, msg, url):
        self._msg.append((msg, url))
        return len(self._msg)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


def mock_get_field_by_name():
    class Field(object):
        max_length = 42
    return (Field(), )
