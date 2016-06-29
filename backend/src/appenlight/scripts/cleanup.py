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
import argparse
from pyramid.paster import setup_logging
from pyramid.paster import bootstrap
from appenlight.celery.tasks import logs_cleanup

log = logging.getLogger(__name__)


def main():
    choices = ['logs']

    parser = argparse.ArgumentParser(description='Cleanup AppEnlight logs')
    parser.add_argument('-c', '--config', required=True,
                        help='Configuration ini file of application')
    parser.add_argument('-t', '--types', choices=choices,
                        default='logs',
                        help='Which parts of database should get cleared')
    parser.add_argument('-r', '--resource', required=True, help='Resource id')
    parser.add_argument('-n', '--namespace', help='Limit to Namespace')
    args = parser.parse_args()

    config_uri = args.config
    setup_logging(config_uri)
    log.setLevel(logging.INFO)
    env = bootstrap(config_uri)

    config = {
        'types': args.types,
        'namespace': args.namespace,
        'resource': int(args.resource),
    }

    action_cleanup_logs(config)


def action_cleanup_logs(config):
    filter_settings = {
        'namespace': []
    }
    if config['namespace']:
        filter_settings['namespace'].append(config['namespace'])
    logs_cleanup(config['resource'], filter_settings)


if __name__ == '__main__':
    main()
