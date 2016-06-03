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

import argparse
import logging
import sys

from alembic.config import Config
from alembic import command
from pyramid.paster import setup_logging, bootstrap
from pyramid.threadlocal import get_current_registry, get_current_request

from appenlight.lib import get_callable
from appenlight.models.services.config import ConfigService

log = logging.getLogger(__name__)


def main(argv=sys.argv):
    parser = argparse.ArgumentParser(
        description='Migrate App Enlight database to latest version',
        add_help=False)
    parser.add_argument('-c', '--config', required=True,
                        help='Configuration ini file of application')
    args = parser.parse_args()
    config_uri = args.config

    setup_logging(config_uri)
    bootstrap(config_uri)
    registry = get_current_registry()
    alembic_cfg = Config()
    alembic_cfg.set_main_option("script_location",
                                "ziggurat_foundations:migrations")
    alembic_cfg.set_main_option("sqlalchemy.url",
                                registry.settings["sqlalchemy.url"])
    command.upgrade(alembic_cfg, "head")
    alembic_cfg = Config()
    alembic_cfg.set_main_option("script_location", "appenlight:migrations")
    alembic_cfg.set_main_option("sqlalchemy.url",
                                registry.settings["sqlalchemy.url"])
    command.upgrade(alembic_cfg, "head")

    for plugin_name, config in registry.appenlight_plugins.items():
        if config['sqlalchemy_migrations']:
            alembic_cfg = Config()
            alembic_cfg.set_main_option("script_location",
                                        config['sqlalchemy_migrations'])
            alembic_cfg.set_main_option("sqlalchemy.url",
                                        registry.settings["sqlalchemy.url"])
            command.upgrade(alembic_cfg, "head")

    with get_current_request().tm:
        ConfigService.setup_default_values()

        for plugin_name, config in registry.appenlight_plugins.items():
            if config['default_values_setter']:
                get_callable(config['default_values_setter'])()
