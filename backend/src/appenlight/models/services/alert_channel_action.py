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
