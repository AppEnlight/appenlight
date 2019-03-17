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

from appenlight.models.plugin_config import PluginConfig
from appenlight.models.services.base import BaseService
from appenlight.models import get_db_session

log = logging.getLogger(__name__)


class PluginConfigService(BaseService):
    @classmethod
    def all(cls, db_session=None):
        db_session = get_db_session(db_session)
        query = db_session.query(PluginConfig)
        return query

    @classmethod
    def by_id(cls, plugin_id, db_session=None):
        db_session = get_db_session(db_session)
        query = db_session.query(PluginConfig)
        query = query.filter(PluginConfig.id == plugin_id)
        return query.first()

    @classmethod
    def by_query(
        cls, resource_id=None, plugin_name=None, section=None, db_session=None
    ):
        db_session = get_db_session(db_session)

        query = db_session.query(PluginConfig)
        if resource_id:
            query = query.filter(PluginConfig.resource_id == resource_id)
        if plugin_name:
            query = query.filter(PluginConfig.plugin_name == plugin_name)
        if section:
            query = query.filter(PluginConfig.section == section)
        return query
