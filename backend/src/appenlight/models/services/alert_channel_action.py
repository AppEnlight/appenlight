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

from appenlight.models import get_db_session
from appenlight.models.alert_channel_action import AlertChannelAction
from appenlight.models.services.base import BaseService


class AlertChannelActionService(BaseService):
    @classmethod
    def by_owner_id_and_pkey(cls, owner_id, pkey, db_session=None):
        db_session = get_db_session(db_session)
        query = db_session.query(AlertChannelAction)
        query = query.filter(AlertChannelAction.owner_id == owner_id)
        return query.filter(AlertChannelAction.pkey == pkey).first()

    @classmethod
    def by_pkey(cls, pkey, db_session=None):
        db_session = get_db_session(db_session)
        query = db_session.query(AlertChannelAction)
        return query.filter(AlertChannelAction.pkey == pkey).first()

    @classmethod
    def by_owner_id_and_type(cls, owner_id, alert_type, db_session=None):
        db_session = get_db_session(db_session)
        query = db_session.query(AlertChannelAction)
        query = query.filter(AlertChannelAction.owner_id == owner_id)
        return query.filter(AlertChannelAction.type == alert_type).first()

    @classmethod
    def by_type(cls, alert_type, db_session=None):
        db_session = get_db_session(db_session)
        query = db_session.query(AlertChannelAction)
        return query.filter(AlertChannelAction.type == alert_type)

    @classmethod
    def by_other_id(cls, other_id, db_session=None):
        db_session = get_db_session(db_session)
        query = db_session.query(AlertChannelAction)
        return query.filter(AlertChannelAction.other_id == other_id)

    @classmethod
    def by_resource_id(cls, resource_id, db_session=None):
        db_session = get_db_session(db_session)
        query = db_session.query(AlertChannelAction)
        return query.filter(AlertChannelAction.resource_id == resource_id)
