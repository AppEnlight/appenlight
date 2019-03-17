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
                conditions.append(
                    sa.and_(
                        Config.key == pair["key"], Config.section == pair["section"]
                    )
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
    def by_key_and_section(
        cls, key, section, auto_create=False, default_value=None, db_session=None
    ):
        db_session = get_db_session(db_session)
        registry = get_current_registry()

        @registry.cache_regions.memory_min_1.cache_on_arguments(
            namespace="ConfigService.by_key_and_section"
        )
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
            config = ConfigService.create_config(key, section, value=default_value)
            cached.invalidate(key, section)
        return config

    @classmethod
    def setup_default_values(self):
        """
        Will add fresh default config values to database if no keys are found
        :return:
        """
        log.info("Checking/setting default values")
        self.by_key_and_section(
            "template_footer_html", "global", default_value="", auto_create=True
        )
        self.by_key_and_section(
            "list_groups_to_non_admins", "global", default_value=True, auto_create=True
        )
        self.by_key_and_section(
            "per_application_reports_rate_limit",
            "global",
            default_value=2000,
            auto_create=True,
        )
        self.by_key_and_section(
            "per_application_logs_rate_limit",
            "global",
            default_value=100000,
            auto_create=True,
        )
        self.by_key_and_section(
            "per_application_metrics_rate_limit",
            "global",
            default_value=100000,
            auto_create=True,
        )
