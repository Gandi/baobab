# -*- coding: utf-8 -*-

from oauth2 import Consumer, Client, Token
from httplib2 import ProxyInfo
from httplib2.socks import PROXY_TYPE_HTTP

from django.conf import settings


class Authentication(object):

    def __init__(self, consumer_key, consumer_secret, token_key, token_secret):
        consumer = Consumer(key=consumer_key, secret=consumer_secret)
        token = Token(key=token_key, secret=token_secret)

        proxy_info = None
        if hasattr(settings, 'PROXY_HOST') and \
                hasattr(settings, 'PROXY_PORT'):
            proxy_info = ProxyInfo(
                proxy_type=PROXY_TYPE_HTTP,
                proxy_host=settings.PROXY_HOST,
                proxy_port=settings.PROXY_PORT)
        self.client = Client(
            consumer=consumer,
            token=token,
            proxy_info=proxy_info)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
