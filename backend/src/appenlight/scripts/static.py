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
import os
import pkg_resources
import shutil

from pyramid.paster import setup_logging
from pyramid.paster import bootstrap

log = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description='Generate App Enlight static resources',
        add_help=False)
    parser.add_argument('-c', '--config', required=True,
                        help='Configuration ini file of application')
    args = parser.parse_args()
    config_uri = args.config
    setup_logging(config_uri)
    env = bootstrap(config_uri)
    registry = env['registry']
    settings = registry.settings
    if os.path.exists(settings['webassets.dir']):
        shutil.rmtree(settings['webassets.dir'])
    os.mkdir(settings['webassets.dir'])
    ae_basedir = pkg_resources.resource_filename('appenlight', 'static')
    shutil.copytree(ae_basedir,
                    os.path.join(settings['webassets.dir'], 'appenlight'))

    for plugin_name, config in registry.appenlight_plugins.items():
        if config['static']:
            shutil.copytree(config['static'],
                            os.path.join(settings['webassets.dir'],
                                         plugin_name))

    for root, dirs, files in os.walk(settings['webassets.dir']):
        for item in dirs:
            os.chmod(os.path.join(root, item), 0o775)
        for item in files:
            os.chmod(os.path.join(root, item), 0o664)
