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

from appenlight.models import get_db_session
from appenlight.models.alert_channel import AlertChannel
from appenlight.models.services.base import BaseService


class AlertChannelService(BaseService):
    @classmethod
    def by_owner_id_and_pkey(cls, owner_id, pkey, db_session=None):
        db_session = get_db_session(db_session)
        query = db_session.query(AlertChannel)
        query = query.filter(AlertChannel.owner_id == owner_id)
        return query.filter(AlertChannel.pkey == pkey).first()

    @classmethod
    def by_integration_id(cls, integration_id, db_session=None):
        db_session = get_db_session(db_session)
        query = db_session.query(AlertChannel)
        query = query.filter(AlertChannel.integration_id == integration_id)
        return query.first()
