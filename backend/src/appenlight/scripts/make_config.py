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
import jinja2
from cryptography.fernet import Fernet


log = logging.getLogger(__name__)


def gen_secret():
    return Fernet.generate_key().decode('utf8')


def main():
    parser = argparse.ArgumentParser(
        description='Generate App Enlight static resources',
        add_help=False)
    parser.add_argument('config', help='Name of generated file')
    parser.add_argument(
        '--domain',
        default='appenlight-rhodecode.local',
        help='Domain which will be used to serve the application')
    parser.add_argument(
        '--dbstring',
        default='postgresql://appenlight:test@127.0.0.1:5432/appenlight',
        help='Domain which will be used to serve the application')
    args = parser.parse_args()
    ini_path = os.path.join('templates', 'ini', 'production.ini.jinja2')
    template_str = pkg_resources.resource_string('appenlight', ini_path)
    template = jinja2.Template(template_str.decode('utf8'))
    template_vars = {'appenlight_encryption_secret': gen_secret(),
                     'appenlight_authtkt_secret': gen_secret(),
                     'appenlight_redis_session_secret': gen_secret(),
                     'appenlight_domain': args.domain,
                     'appenlight_dbstring': args.dbstring,
                     }
    compiled = template.render(**template_vars)
    with open(args.config, 'w') as f:
        f.write(compiled)
