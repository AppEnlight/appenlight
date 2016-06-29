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

import sqlalchemy as sa
from pyramid.threadlocal import get_current_registry

from appenlight.models.config import Config
from appenlight.models.services.base import BaseService
from appenlight.models import get_db_session

log = logging.getLogger(__name__)


class ConfigService(BaseService):
    @classmethod
    def all(cls, db_session=None):
        db_session = get_db_session(db_session)
        query = db_session.query(Config)
        return query

    @classmethod
    def filtered_key_and_section(cls, pairs=None, db_session=None):
        db_session = get_db_session(db_session)
        query = db_session.query(Config)
        if pairs:
            conditions = []
            for pair in pairs:
                conditions.append(sa.and_(
                    Config.key == pair['key'],
                    Config.section == pair['section'])
                )

            query = query.filter(sa.or_(*conditions))
        return query

    @classmethod
    def create_config(cls, key, section, value=None, db_session=None):
        config = Config(key=key, section=section, value=value)
        db_session = get_db_session(db_session)
        db_session.add(config)
        db_session.flush()
        return config

    @classmethod
    def by_key_and_section(cls, key, section, auto_create=False,
                           default_value=None, db_session=None):
        db_session = get_db_session(db_session)
        registry = get_current_registry()

        @registry.cache_regions.memory_min_1.cache_on_arguments(
            namespace='ConfigService.by_key_and_section')
        def cached(key, section):
            query = db_session.query(Config).filter(Config.key == key)
            query = query.filter(Config.section == section)
            config = query.first()
            if config:
                db_session.expunge(config)
            return config

        config = cached(key, section)
        if config:
            config = db_session.merge(config, load=False)
        if config is None and auto_create:
            config = ConfigService.create_config(key, section,
                                                 value=default_value)
            cached.invalidate(key, section)
        return config

    @classmethod
    def setup_default_values(self):
        """
        Will add fresh default config values to database if no keys are found
        :return:
        """
        log.info('Checking/setting default values')
        self.by_key_and_section('template_footer_html', 'global',
                                default_value='', auto_create=True)
        self.by_key_and_section('list_groups_to_non_admins', 'global',
                                default_value=True, auto_create=True)
        self.by_key_and_section('per_application_reports_rate_limit', 'global',
                                default_value=2000, auto_create=True)
        self.by_key_and_section('per_application_logs_rate_limit', 'global',
                                default_value=100000, auto_create=True)
        self.by_key_and_section('per_application_metrics_rate_limit', 'global',
                                default_value=100000, auto_create=True)
