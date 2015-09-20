# -*- coding: utf-8 -*-

from __future__ import absolute_import

# import inspect  # needed by cmd_help
import logging
import os
import select
import signal
import socket
import ssl
from time import sleep

from irc import connection
from irc.client import (IRC as IRCClient,
                        ServerNotConnectedError,
                        ServerConnectionError,
                        is_channel)

from django.conf import settings

from .base import SocialNetworkBase, UnPublishedException

LOG = logging.getLogger(__name__)


class IRC(SocialNetworkBase):

    """
    send the message through a unix socket to the client irc daemon
    """

    name = 'irc'

    @classmethod
    def is_configured(cls):
        if not (hasattr(settings, 'IRC') and
                hasattr(settings, 'IRC_SOCKET_PATH') and
                hasattr(settings, 'IRC_ALLOWED_CHAR')):
            return False
        for conf in settings.IRC:
            if not (conf.get('nick') and
                    conf.get('server') and
                    conf.get('channels')):
                return False
            for chan in conf['channels']:
                if not ('name' in chan and is_channel(chan['name'])):
                    return False
        return True

    @classmethod
    def get_max_char(cls, default):
        if cls.is_configured():
            return settings.IRC_ALLOWED_CHAR
        return default

    def __init__(self):
        if not self.is_configured():
            raise RuntimeError('IRC is not configured')
        self.send_msg = None

    def __enter__(self):
        self.send_msg = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        self.send_msg.connect(settings.IRC_SOCKET_PATH)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.send_msg.close()
        self.send_msg = None

    def publish(self, msg, url):
        if not self.send_msg:
            raise UnPublishedException(
                'msg: %s is not send to IRC not connected' % msg)
        try:
            self.send_msg.send('%s\0%s' % (msg, url))
        except Exception as err:
            raise UnPublishedException('Cannot send to msg through irc: %s' %
                                       err)
        return ''


class IRCDaemon(object):

    """
    a client irc daemon which received the message to send from a socket unix
    """

    def __init__(self):
        if not IRC.is_configured():
            raise RuntimeError('IRCDaemon is not configured')
        if os.path.exists(settings.IRC_SOCKET_PATH):
            os.remove(settings.IRC_SOCKET_PATH)
        self.is_alive = False

        self.get_msg = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        self.get_msg.bind(settings.IRC_SOCKET_PATH)

        self.client = IRCClient()
        for conf in settings.IRC:
            try:
                server = self.client.server()
                server.gandi_conf = conf

                for elem in dir(self):
                    if elem.startswith('on_'):
                        server.add_global_handler(elem[3:],
                                                  getattr(self, elem))

                if conf.get('ssl', False):
                    connection_factory = connection.Factory(
                        wrapper=ssl.wrap_socket)
                else:
                    connection_factory = connection.Factory()
                server.connect(conf.get('server'), conf.get('port', 6667),
                               conf.get('nick'), conf.get('password'),
                               conf.get('username'), conf.get('ircname'),
                               connection_factory)

            except ServerConnectionError as err:
                LOG.error(err)

        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGQUIT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)

    @property
    def servers(self):
        return self.client.connections

    def run(self):
        LOG.info('server running')
        self.is_alive = True
        while self.is_alive:
            try:
                self.client.process_once()
                data = self.get_msg_to_publish()
                if data:
                    for server in self.servers:
                        chans = [chan['name'] for chan in
                                 server.gandi_conf['channels']]
                        prefix = server.gandi_conf.get('prefix')
                        if prefix:
                            server.privmsg_many(chans, '%s %s %s' % (
                                prefix, data[0], data[1]))
                        else:
                            server.privmsg_many(chans, '%s %s' % (
                                data[0], data[1]))
                sleep(0.2)
            except ServerNotConnectedError as err:
                LOG.error('not connected %s %s', err, dir(err))
            except Exception as exc:
                LOG.error(exc)
        for server in self.servers:
            server.disconnect(server.gandi_conf.get('on_quit'))
        self.get_msg.close()
        os.remove(settings.IRC_SOCKET_PATH)

    def get_msg_to_publish(self):
        reads = select.select([self.get_msg, ], [], [], 0)[0]
        if reads:
            return self.get_msg.recv(IRC.get_max_char(256)).split('\0')
        return None

    def shutdown(self, *args, **kwargs):
        self.is_alive = False
        LOG.info('Shutting down ...')

    def reconnect(self, server, delay=10):
        try:
            name = server.get_server_name() or server.gandi_conf['server']
            LOG.info('Try to reconnect to: %s', name)
            server.reconnect()
        except ServerConnectionError as err:
            pass
        except Exception as exc:
            LOG.error(exc)
        if not server.is_connected():
            LOG.info('re-connection for %s failed, will retry in %d sec',
                     name, delay)
            self.client.execute_delayed(delay, self.reconnect,
                                        (server, delay*2))

    # available cmd

    # def cmd_help(self, *args):
    #     """to get the available command"""
    #     if args and hasattr(self, 'cmd_%s' % args[0]):
    #         func = getattr(self, 'cmd_%s' % args[0])
    #         return inspect.getdoc(func).split('\n')
    #     else:
    #         res = []
    #         for elem in dir(self):
    #             if elem.startswith('cmd_'):
    #                 func = getattr(self, elem)
    #                 res.append('%s: %s' % (
    #                     elem[4:], func.__doc__.split('\n')[0]))
    #         return res

    # IRC EVENT

    def on_welcome(self, server, event):
        for chan in server.gandi_conf['channels']:
            LOG.info('connected to %s will now join %s',
                     server.get_server_name(), chan['name'])
            server.join(chan['name'], chan.get('password', ''))
            server.privmsg(chan['name'], server.gandi_conf.get('on_welcome'))

    def on_disconnect(self, server, event):
        if self.is_alive:
            LOG.info('disconnected from server: %s',
                     server.get_server_name() or server.gandi_conf['server'])
            self.reconnect(server)

    def on_error(self, server, event):
        LOG.error('on server: %s type: %s, source: %s, target: %s, args: %s',
                  server.get_server_name() or server.gandi_conf['server'],
                  event.type,
                  event.source.nick,
                  event.target,
                  event.arguments)

    def on_privnotice(self, server, event):
        LOG.info('on server: %s type: %s, source: %s, target: %s, args: %s',
                 server.get_server_name() or server.gandi_conf['server'],
                 event.type,
                 event.source.nick,
                 event.target,
                 event.arguments)

    on_pubnotice = on_privnotice

    def _handle_msg(self, server, event):
        """
        handle each message received, this give the possibility the respond
        to some command
        """
        msg = event.arguments[0].split()
        if msg[0].startswith(server.get_nickname()) or \
           event.target == server.get_nickname():
            LOG.info('on server: %s, nick: %s, send cmd: %s with msg: %s',
                     server.get_server_name(),
                     event.source.nick,
                     event.type,
                     event.arguments)
            if msg[0].startswith(server.get_nickname()):
                del msg[0]
            cmd = msg if msg else ['help', ]
            func = getattr(self, 'cmd_%s' % cmd[0], None)
            if func:
                return func(*cmd[1:])
        elif server.get_nickname() in msg:
            LOG.info('on server: %s, nick: %s highlighted the bot with: %s',
                     server.get_server_name(),
                     event.source.nick,
                     event.arguments)
        return []

    def on_pubmsg(self, server, event):
        msg = self._handle_msg(server, event)
        if msg:
            for line in msg:
                server.privmsg(event.target, line)

    def on_privmsg(self, server, event):
        msg = self._handle_msg(server, event)
        if msg:
            for line in msg:
                server.privmsg(event.source.nick, msg)
