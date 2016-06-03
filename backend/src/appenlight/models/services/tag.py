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

import sqlalchemy as sa
from appenlight.lib.ext_json import json
from pyramid.threadlocal import get_current_registry
from appenlight.models.tag import Tag
from appenlight.models.services.base import BaseService
from appenlight.models import get_db_session


class TagService(BaseService):
    @classmethod
    def cut_name(cls, tag_name):
        return tag_name[:32]

    @classmethod
    def cut_value(cls, value):
        if isinstance(value, str):
            value = value[:128]
        return value

    @classmethod
    def by_resource_id_and_value(cls, resource_id, tag_name, value,
                                 db_session=None, create_missing=True):
        """
        Fetches tag and creates a new one if missing
        """
        db_session = get_db_session(db_session)
        registry = get_current_registry()

        @registry.cache_regions.redis_min_10.cache_on_arguments(
            namespace='TagService.by_resource_id_and_value')
        def cached(resource_id, tag_name, value):
            reduced_name = cls.cut_name(tag_name.decode('utf8'))
            reduced_value = cls.cut_value(value.decode('utf8'))

            query = db_session.query(Tag)
            query = query.filter(Tag.resource_id == resource_id)
            query = query.filter(Tag.name == reduced_name)
            query = query.filter(sa.cast(Tag.value, sa.types.TEXT) ==
                                 sa.cast(json.dumps(reduced_value),
                                         sa.types.TEXT))
            tag = query.first()
            if tag:
                db_session.expunge(tag)
            return tag

        view = cached(resource_id, tag_name.encode('utf8'),
                      value.encode('utf8'))
        if not view and create_missing:
            view = cls.create_tag(resource_id,
                                  cls.cut_name(tag_name),
                                  cls.cut_value(value),
                                  db_session)
            cached.invalidate(resource_id, tag_name.encode('utf8'),
                              value.encode('utf8'))
        return view

    @classmethod
    def create_tag(cls, resource_id, tag_name, value, db_session=None):

        tag = Tag(resource_id=resource_id,
                  name=cls.cut_name(tag_name),
                  value=cls.cut_value(value))
        db_session = get_db_session(db_session)
        db_session.add(tag)
        db_session.flush()
        return tag

    @classmethod
    def by_tag_id(cls, tag_id, db_session=None):
        db_session = get_db_session(db_session)
        registry = get_current_registry()

        @registry.cache_regions.redis_min_10.cache_on_arguments(
            namespace='TagService.by_tag_id')
        def cached(tag_id):
            tag = db_session.query(Tag).filter(Tag.id == tag_id).first()
            if tag:
                db_session.expunge(tag)
            return tag

        return cached(tag_id)
