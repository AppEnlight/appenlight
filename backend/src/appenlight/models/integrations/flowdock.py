# -*- coding: utf-8 -*-

# Copyright (C) 2010-2016  RhodeCode GmbH
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License, version 3
# (only), as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# This program is dual-licensed. If you wish to learn more about the
# App Enlight Enterprise Edition, including its added features, Support
# services, and proprietary license terms, please see
# https://rhodecode.com/licenses/

import logging

import requests
from requests.auth import HTTPBasicAuth
import simplejson as json

from appenlight.models.integrations import (IntegrationBase,
                                            IntegrationException)

_ = str

log = logging.getLogger(__name__)


class NotFoundException(Exception):
    pass


class FlowdockIntegration(IntegrationBase):
    __mapper_args__ = {
        'polymorphic_identity': 'flowdock'
    }
    front_visible = False
    as_alert_channel = True
    supports_report_alerting = True
    action_notification = True
    integration_action = 'Message via Flowdock'

    @classmethod
    def create_client(cls, api_token):
        client = FlowdockClient(api_token)
        return client


class FlowdockClient(object):
    def __init__(self, api_token):
        self.auth = HTTPBasicAuth(api_token, '')
        self.api_token = api_token
        self.api_url = 'https://api.flowdock.com/v1/messages'

    def make_request(self, url, method='get', data=None):
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'appenlight-flowdock',
        }
        try:
            if data:
                data = json.dumps(data)
            resp = getattr(requests, method)(url, data=data, headers=headers,
                                             timeout=10)
        except Exception as e:
            raise IntegrationException(
                _('Error communicating with Flowdock: %s') % (e,))
        if resp.status_code > 299:
            raise IntegrationException(resp.text)
        return resp

    def send_to_chat(self, payload):
        url = '%(api_url)s/chat/%(api_token)s' % {'api_url': self.api_url,
                                                  'api_token': self.api_token}
        return self.make_request(url, method='post', data=payload).json()

    def send_to_inbox(self, payload):
        f_args = {'api_url': self.api_url, 'api_token': self.api_token}
        url = '%(api_url)s/team_inbox/%(api_token)s' % f_args
        return self.make_request(url, method='post', data=payload).json()
