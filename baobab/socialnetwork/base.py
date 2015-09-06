# -*- coding: utf-8 -*-

import logging

from django.conf import settings

from baobab.backoffice.models import (Event as BackOfficeEvent,
                                      EventLog as BackOfficeEventLog)
from baobab.socialnetwork.models import (Event as SnEvent,
                                         EventLog as SnEventLog)

LOG = logging.getLogger(__name__)


class UnPublishedException(Exception):
    pass


class SocialNetworks(object):

    _max_char = None

    def __init__(self):
        self. _social_networks = []
        for cls_sn in SocialNetworkBase.__subclasses__():
            try:
                if not cls_sn.name:
                    raise NotImplementedError('%s has no name' % cls_sn)
                self._social_networks.append(cls_sn())
            except Exception as err:
                LOG.error("Couldn't init %s (%s)", cls_sn, err)

    @classmethod
    def get_max_char(cls):
        if not cls._max_char:
            event = BackOfficeEvent._meta.get_field_by_name('msg')[0]
            eventlog = BackOfficeEventLog._meta.get_field_by_name('msg')[0]
            if event.max_length != eventlog.max_length:
                raise RuntimeError(
                    'BackOfficeEvent.msg and BackOfficeEventLog.msg '
                    'HAS TO have the same max length')
            default = event.max_length
            max_chars = []
            for cls_sn in SocialNetworkBase.__subclasses__():
                max_chars.append(cls_sn.get_max_char(default))
            cls._max_char = min(max_chars)
        return cls._max_char

    def publish(self, obj):
        """
        publish msg to all defined SocialNetwork

        :param obj: instance of a django's model
        :type obj: BackOfficeEvent or BackOfficeEventLog
        """
        if not obj.msg:
            return
        for sn in self._social_networks:
            try:
                if not self._is_publish(obj, sn.name):
                    msg = obj.msg
                    if isinstance(obj, BackOfficeEvent):
                        event_id = obj.id
                    else:
                        event_id = obj.event_id
                    url = self._get_url_event(event_id)
                    sn_id = sn.publish(msg, url)
                    LOG.info('publish sn: %s msg: %s, url: %s',
                             sn.name, msg, url)
                    self._mark_as_publish(obj, sn.name, sn_id)
            except Exception as err:
                LOG.error("Can't publish msg: %s, event_id: %d "
                          'for sn: %s (%s)', msg, event_id, sn.name, err)

    def _is_publish(self, obj, sn_name):
        """
        :param obj: instance of a django's model
        :type obj: BackOfficeEvent or BackOfficeEventLog
        :param sn_name: name of the socialnetwork to check
        :type sn_name: string

        :rtype: bool
        """

        if isinstance(obj, BackOfficeEvent):
            if SnEvent.objects.filter(event=obj, name=sn_name).exists():
                return True
        else:
            if SnEventLog.objects.filter(eventlog=obj,
                                         name=sn_name).exists():
                return True
        return False

    def _mark_as_publish(self, obj, sn_name, sn_id):
        """
        :param obj: instance of a django's model
        :type obj: BackOfficeEvent or BackOfficeEventLog
        :param sn_name: name of the socialnetwork
        :type sn_name: string
        :param sn_id: socialNetwork id (if any)
        :type sn_id: str
        """

        if isinstance(obj, BackOfficeEvent):
            SnEvent.objects.create(
                event=obj,
                name=sn_name,
                sn_id=sn_id,
            )
        else:
            SnEventLog.objects.create(
                eventlog=obj,
                name=sn_name,
                sn_id=sn_id,
            )

    def _get_url_event(self, event_id):
        """
        return the url of the event

        :rtype: str
        """
        if hasattr(settings, 'URL_EVENT'):
            return '%s/%d' % (settings.URL_EVENT.rstrip('/'), event_id)
        return ''


class SocialNetworkBase(object):

    """
    interface for all social network, each social network have to
    inherited from this class
    """

    name = None

    @classmethod
    def is_configured(cls):
        raise NotImplementedError()

    @classmethod
    def get_max_char(cls, default):
        raise NotImplementedError()

    def publish(self, msg, url):
        """
        should raise if it failed
        """
        raise NotImplementedError()
