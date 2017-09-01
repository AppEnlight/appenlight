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

from appenlight.models.integrations import (IntegrationBase,
                                            IntegrationException)
from appenlight.lib.ext_json import json

_ = str

log = logging.getLogger(__name__)


class NotFoundException(Exception):
    pass


class SlackIntegration(IntegrationBase):
    __mapper_args__ = {
        'polymorphic_identity': 'slack'
    }
    front_visible = False
    as_alert_channel = True
    supports_report_alerting = True
    action_notification = True
    integration_action = 'Message via Slack'

    @classmethod
    def create_client(cls, api_token):
        client = SlackClient(api_token)
        return client


class SlackClient(object):
    def __init__(self, api_url):
        self.api_url = api_url

    def make_request(self, data=None):
        headers = {
            'User-Agent': 'appenlight-slack',
            'Content-Type': 'application/json'
        }
        try:
            resp = getattr(requests, 'post')(self.api_url,
                                             data=json.dumps(data),
                                             headers=headers,
                                             timeout=3)
        except Exception as e:
            raise IntegrationException(
                _('Error communicating with Slack: %s') % (e,))
        if resp.status_code != requests.codes.ok:
            msg = 'Error communicating with Slack - status code: %s'
            raise IntegrationException(msg % resp.status_code)
        return resp

    def send(self, payload):
        return self.make_request('/rooms/message', method='post',
                                 data=payload).json()
