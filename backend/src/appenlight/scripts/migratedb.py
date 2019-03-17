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
        description="Migrate AppEnlight database to latest version", add_help=False
    )
    parser.add_argument(
        "-c", "--config", required=True, help="Configuration ini file of application"
    )
    args = parser.parse_args()
    config_uri = args.config

    setup_logging(config_uri)
    bootstrap(config_uri)
    registry = get_current_registry()
    alembic_cfg = Config()
    alembic_cfg.set_main_option("sqlalchemy.echo", "true")
    alembic_cfg.set_main_option("script_location", "ziggurat_foundations:migrations")
    alembic_cfg.set_main_option("sqlalchemy.url", registry.settings["sqlalchemy.url"])
    command.upgrade(alembic_cfg, "head")
    alembic_cfg = Config()
    alembic_cfg.set_main_option("sqlalchemy.echo", "true")
    alembic_cfg.set_main_option("script_location", "appenlight:migrations")
    alembic_cfg.set_main_option("sqlalchemy.url", registry.settings["sqlalchemy.url"])
    command.upgrade(alembic_cfg, "head")

    for plugin_name, config in registry.appenlight_plugins.items():
        if config["sqlalchemy_migrations"]:
            alembic_cfg = Config()
            alembic_cfg.set_main_option(
                "script_location", config["sqlalchemy_migrations"]
            )
            alembic_cfg.set_main_option(
                "sqlalchemy.url", registry.settings["sqlalchemy.url"]
            )
            alembic_cfg.set_main_option("sqlalchemy.echo", "true")
            command.upgrade(alembic_cfg, "head")

    with get_current_request().tm:
        ConfigService.setup_default_values()

        for plugin_name, config in registry.appenlight_plugins.items():
            if config["default_values_setter"]:
                get_callable(config["default_values_setter"])()
