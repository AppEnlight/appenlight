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
# AppEnlight Enterprise Edition, including its added features, Support
# services, and proprietary license terms, please see
# https://rhodecode.com/licenses/

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
