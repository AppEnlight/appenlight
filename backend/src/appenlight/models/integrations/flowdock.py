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
from requests.auth import HTTPBasicAuth
import simplejson as json

from appenlight.models.integrations import IntegrationBase, IntegrationException

_ = str

log = logging.getLogger(__name__)


class NotFoundException(Exception):
    pass


class FlowdockIntegration(IntegrationBase):
    __mapper_args__ = {"polymorphic_identity": "flowdock"}
    front_visible = False
    as_alert_channel = True
    supports_report_alerting = True
    action_notification = True
    integration_action = "Message via Flowdock"

    @classmethod
    def create_client(cls, api_token):
        client = FlowdockClient(api_token)
        return client


class FlowdockClient(object):
    def __init__(self, api_token):
        self.auth = HTTPBasicAuth(api_token, "")
        self.api_token = api_token
        self.api_url = "https://api.flowdock.com/v1/messages"

    def make_request(self, url, method="get", data=None):
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "appenlight-flowdock",
        }
        try:
            if data:
                data = json.dumps(data)
            resp = getattr(requests, method)(
                url, data=data, headers=headers, timeout=10
            )
        except Exception as e:
            raise IntegrationException(
                _("Error communicating with Flowdock: %s") % (e,)
            )
        if resp.status_code > 299:
            raise IntegrationException(resp.text)
        return resp

    def send_to_chat(self, payload):
        url = "%(api_url)s/chat/%(api_token)s" % {
            "api_url": self.api_url,
            "api_token": self.api_token,
        }
        return self.make_request(url, method="post", data=payload).json()

    def send_to_inbox(self, payload):
        f_args = {"api_url": self.api_url, "api_token": self.api_token}
        url = "%(api_url)s/team_inbox/%(api_token)s" % f_args
        return self.make_request(url, method="post", data=payload).json()
