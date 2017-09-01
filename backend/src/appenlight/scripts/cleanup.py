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
