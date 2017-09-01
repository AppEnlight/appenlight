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

from requests.exceptions import HTTPError, ConnectionError
from camplight import Request, Campfire
from camplight.exceptions import CamplightException

from appenlight.models.integrations import (IntegrationBase,
                                            IntegrationException)

_ = str

log = logging.getLogger(__name__)


class NotFoundException(Exception):
    pass


class CampfireIntegration(IntegrationBase):
    __mapper_args__ = {
        'polymorphic_identity': 'campfire'
    }
    front_visible = False
    as_alert_channel = True
    supports_report_alerting = True
    action_notification = True
    integration_action = 'Message via Campfire'

    @classmethod
    def create_client(cls, api_token, account):
        client = CampfireClient(api_token, account)
        return client


class CampfireClient(object):
    def __init__(self, api_token, account):
        request = Request('https://%s.campfirenow.com' % account, api_token)
        self.campfire = Campfire(request)

    def get_account(self):
        try:
            return self.campfire.account()
        except (HTTPError, CamplightException) as e:
            raise IntegrationException(str(e))

    def get_rooms(self):
        try:
            return self.campfire.rooms()
        except (HTTPError, CamplightException) as e:
            raise IntegrationException(str(e))

    def speak_to_room(self, room, message, sound='RIMSHOT'):
        try:
            room = self.campfire.room(room)
            room.join()
            room.speak(message, type_='TextMessage')
        except (HTTPError, CamplightException, ConnectionError) as e:
            raise IntegrationException(str(e))
