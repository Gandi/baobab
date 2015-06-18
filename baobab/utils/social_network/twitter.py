# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import json
import logging
import pytz
import urllib

from django.conf import settings

from .authentication import Authentication

LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARNING)


class Twitter(Authentication):

    url_api = None
    rate_limit = {}
    manual_rate_limit = {
        # '%s/statuses/update.json' % url_api: {
        #     'max_request': 15,
        #     'window_request': 15,  # in minutes
        #     'request_done': 0,
        #     'request_window': None,
        # },
    }

    @classmethod
    def is_configured(cls):
        return all([
            hasattr(settings, 'TWITTER_CONSUMER_KEY'),
            hasattr(settings, 'TWITTER_CONSUMER_SECRET'),
            hasattr(settings, 'TWITTER_ACCESS_TOKEN'),
            hasattr(settings, 'TWITTER_ACCESS_TOKEN_SECRET'),
            hasattr(settings, 'TWITTER_URL_API'),
        ])

    def __init__(self):
        if not self.is_configured():
            raise RuntimeError('Twitter is not configured')
        if not self.url_api:
            self.url_api = settings.TWITTER_URL_API.rstrip('/')
        super(Twitter, self).__init__(settings.TWITTER_CONSUMER_KEY,
                                      settings.TWITTER_CONSUMER_SECRET,
                                      settings.TWITTER_ACCESS_TOKEN,
                                      settings.TWITTER_ACCESS_TOKEN_SECRET)

    def _get_url_event(self, event_id):
        if hasattr(settings, 'URL_EVENT'):
            return '%s/%d' % (settings.URL_EVENT.rstrip('/'), event_id)
        return ''

    def _do_manual_rate_limit(self, url):
        limit = self.manual_rate_limit.get(url, None)
        if not limit:
            return
        if not limit['request_window'] or \
                limit['request_window'] < datetime.now(pytz.timezone('UTC')):
            minutes = limit['window_request']
            limit['request_window'] = (datetime.now(pytz.timezone('UTC')) +
                                       timedelta(minutes=minutes))
            limit['request_done'] = 1
        else:
            limit['request_done'] += 1
        if limit['request_done'] == limit['max_request']:
            self.rate_limit[url] = limit['request_window']
            LOG.warning('Rate limit will be exceeded for: %s', url)

    def _request(self, url, method='GET', body='', msg_err=''):
        if self.is_rate_limited(url):
            return None
        try:
            resp, content = self.client.request(url, method=method,
                                                body=urllib.urlencode(body))
            if resp['status'] == '200':
                remaining = resp.get('x-rate-limit-remaining')
                if remaining and remaining == '0':
                    self.rate_limit[url] = datetime.fromtimestamp(
                        int(resp['x-rate-limit-reset']), pytz.timezone('UTC'))
                    LOG.warning('Rate limit will be exceeded for: %s', url)
                if not remaining:
                    self._do_manual_rate_limit(url)
                return json.loads(content)
            try:
                data = json.loads(content)
                if resp['status'] == '403' and \
                        data['errors'][0]['code'] == 187:
                    LOG.warning('Duplicate status')
                    return self.get_last_msg()
                if resp['status'] == '429' and \
                        data['errors'][0]['code'] == 88:
                    self.rate_limit[url] = datetime.fromtimestamp(
                        int(resp['x-rate-limit-reset']), pytz.timezone('UTC'))
                    LOG.warning('Rate limit exceeded for: %s', url)
                    return None
                LOG.error('%s, http_error_code: %s, twitter_msg: %s, '
                          'twitter_code: %s', msg_err, resp['status'],
                          data['errors'][0]['message'],
                          data['errors'][0]['code'])
            except ValueError:
                LOG.error('JSON: %s: %s, %s', msg_err, resp, content)
        except Exception as err:
            LOG.error('%s: %s', msg_err, err)
        return None

    def is_rate_limited(self, url):
        date = self.rate_limit.get(url)
        if date and date < datetime.now(pytz.timezone('UTC')):
            date = None
            del self.rate_limit[url]
        return isinstance(date, datetime)

    def create(self, status, event_id):
        url = '%s/statuses/update.json' % self.url_api
        body = {'status': '%s %s' % (status, self._get_url_event(event_id))}
        msg_err = 'Create new tweet for event_id %d' % event_id
        content = self._request(url, method='POST', body=body, msg_err=msg_err)
        if content:
            return content['id_str']
        return None

    def get_msg(self, msg_id):
        if not msg_id:
            return ''
        url = '%s/statuses/show.json' % self.url_api
        body = {'id': msg_id}
        msg_err = 'Reading a tweet msg_id: %d' % msg_id
        content = self._request(url, method='GET', body=body, msg_err=msg_err)
        if content:
            return content['text']
        return ''

    def get_last_msg(self):
        url = '%s/account/verify_credentials.json' % self.url_api
        msg_err = 'Getting last tweet'
        content = self._request(url, method='GET', msg_err=msg_err)
        if content:
            return content['status']
        return None
