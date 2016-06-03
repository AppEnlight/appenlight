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

from . import IntegrationBase, IntegrationException

_ = str

log = logging.getLogger(__name__)


class NotFoundException(Exception):
    pass


class HipchatIntegration(IntegrationBase):
    __mapper_args__ = {
        'polymorphic_identity': 'hipchat'
    }
    front_visible = False
    as_alert_channel = True
    supports_report_alerting = True
    action_notification = True
    integration_action = 'Message via Hipchat'

    @classmethod
    def create_client(cls, api_token):
        client = HipchatClient(api_token)
        return client


class HipchatClient(object):
    def __init__(self, api_token):
        self.api_token = api_token
        self.api_url = 'https://api.hipchat.com/v1'

    def make_request(self, endpoint, method='get', data=None):
        headers = {
            'User-Agent': 'appenlight-hipchat',
        }
        url = '%s%s' % (self.api_url, endpoint)
        params = {
            'format': 'json',
            'auth_token': self.api_token
        }
        try:
            resp = getattr(requests, method)(url, data=data, headers=headers,
                                             params=params,
                                             timeout=3)
        except Exception as e:
            msg = 'Error communicating with Hipchat: %s'
            raise IntegrationException(_(msg) % (e,))
        if resp.status_code == 404:
            msg = 'Error communicating with Hipchat - Room not found'
            raise IntegrationException(msg)
        elif resp.status_code != requests.codes.ok:
            msg = 'Error communicating with Hipchat - status code: %s'
            raise IntegrationException(msg % resp.status_code)
        return resp

    def get_rooms(self):
        # not used with notification api token
        return self.make_request('/rooms/list')

    def send(self, payload):
        return self.make_request('/rooms/message', method='post',
                                 data=payload).json()
