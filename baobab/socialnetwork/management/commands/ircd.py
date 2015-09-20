# -*- coding: utf-8 -*-
"""
daemon irc
"""

from django.core.management.base import BaseCommand

from baobab.socialnetwork.irc import IRCDaemon


class Command(BaseCommand):

    help = "A IRC daemon"

    def handle(self, *args, **options):
        irc = IRCDaemon()
        irc.run()
