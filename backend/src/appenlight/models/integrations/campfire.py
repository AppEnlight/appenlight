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
