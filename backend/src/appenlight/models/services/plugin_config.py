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
    def by_query(cls, resource_id=None, plugin_name=None,
                 section=None, db_session=None):
        db_session = get_db_session(db_session)

        query = db_session.query(PluginConfig)
        if resource_id:
            query = query.filter(PluginConfig.resource_id == resource_id)
        if plugin_name:
            query = query.filter(PluginConfig.plugin_name == plugin_name)
        if section:
            query = query.filter(PluginConfig.section == section)
        return query
