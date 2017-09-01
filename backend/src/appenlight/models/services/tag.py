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
