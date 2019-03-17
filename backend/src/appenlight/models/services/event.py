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

import sqlalchemy as sa
from pyramid.threadlocal import get_current_registry
from paginate_sqlalchemy import SqlalchemyOrmPage
from ziggurat_foundations.models.services.user import UserService

from appenlight.models import get_db_session
from appenlight.models.event import Event
from appenlight.models.services.base import BaseService


class EventService(BaseService):
    @classmethod
    def for_resource(
        cls,
        resource_ids,
        event_type=None,
        status=None,
        since_when=None,
        limit=20,
        event_id=None,
        target_uuid=None,
        order_by=None,
        or_target_user_id=None,
        db_session=None,
    ):
        """
        Fetches events including based on passed params OR if target_user_id
        is present include events that just target this user
        """
        db_session = get_db_session(db_session)
        query = db_session.query(Event)
        query = query.options(sa.orm.joinedload(Event.resource))
        and_cond = [Event.resource_id.in_(resource_ids)]
        if not resource_ids:
            and_cond = [Event.resource_id == -999]

        if event_type:
            and_cond.append(Event.event_type == event_type)
        if status:
            and_cond.append(Event.status == status)
        if since_when:
            and_cond.append(Event.start_date >= since_when)
        if event_id:
            and_cond.append(Event.id == event_id)
        if target_uuid:
            and_cond.append(Event.target_uuid == target_uuid)

        or_cond = []

        if or_target_user_id:
            or_cond.append(sa.or_(Event.target_user_id == or_target_user_id))

        query = query.filter(sa.or_(sa.and_(*and_cond), *or_cond))
        if not order_by:
            query = query.order_by(sa.desc(Event.start_date))
        if limit:
            query = query.limit(limit)

        return query

    @classmethod
    def by_type_and_status(
        cls,
        event_types,
        status_types,
        since_when=None,
        older_than=None,
        db_session=None,
        app_ids=None,
    ):
        db_session = get_db_session(db_session)
        query = db_session.query(Event)
        query = query.filter(Event.event_type.in_(event_types))
        query = query.filter(Event.status.in_(status_types))
        if since_when:
            query = query.filter(Event.start_date >= since_when)
        if older_than:
            query = query.filter(Event.start_date <= older_than)
        if app_ids:
            query = query.filter(Event.resource_id.in_(app_ids))
        return query

    @classmethod
    def latest_for_user(cls, user, db_session=None):
        registry = get_current_registry()
        resources = UserService.resources_with_perms(
            user, ["view"], resource_types=registry.resource_types
        )
        resource_ids = [r.resource_id for r in resources]
        db_session = get_db_session(db_session)
        return EventService.for_resource(
            resource_ids, or_target_user_id=user.id, limit=10, db_session=db_session
        )

    @classmethod
    def get_paginator(
        cls,
        user,
        page=1,
        item_count=None,
        items_per_page=50,
        order_by=None,
        filter_settings=None,
        db_session=None,
    ):
        if not filter_settings:
            filter_settings = {}
        registry = get_current_registry()
        resources = UserService.resources_with_perms(
            user, ["view"], resource_types=registry.resource_types
        )
        resource_ids = [r.resource_id for r in resources]
        query = EventService.for_resource(
            resource_ids, or_target_user_id=user.id, limit=100, db_session=db_session
        )

        paginator = SqlalchemyOrmPage(
            query, page=page, items_per_page=items_per_page, **filter_settings
        )
        return paginator
