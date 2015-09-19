# -*- coding: utf-8 -*-


class MockLOG(object):

    def __init__(self):
        self._info = []
        self._error = []

    def info(self, msg, *args):
        self._info.append(msg % args)

    def error(self, msg, *args):
        self._error.append(msg % args)
