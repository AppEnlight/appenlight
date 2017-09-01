# -*- coding: utf-8 -*-

# Copyright 2010 - 2017 RhodeCode GmbH and the AppEnlight project authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
