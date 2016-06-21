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

import logging

from datetime import timedelta
from celery import Celery
from celery.bin import Option
from celery.schedules import crontab
from celery.signals import worker_init, task_revoked, user_preload_options
from celery.signals import task_prerun, task_retry, task_failure, task_success
from kombu.serialization import register
from pyramid.paster import bootstrap
from pyramid.request import Request
from pyramid.scripting import prepare
from pyramid.settings import asbool
from pyramid.threadlocal import get_current_request

from appenlight.celery.encoders import json_dumps, json_loads
from appenlight_client.ext.celery import register_signals

log = logging.getLogger(__name__)

register('date_json', json_dumps, json_loads,
         content_type='application/x-date_json',
         content_encoding='utf-8')

celery = Celery()

celery.user_options['preload'].add(
    Option('--ini', dest='ini', default=None,
           help='Specifies pyramid configuration file location.')
)


@user_preload_options.connect
def on_preload_parsed(options, **kwargs):
    """
    This actually configures celery from pyramid config file
    """
    celery.conf['INI_PYRAMID'] = options['ini']
    import appenlight_client.client as e_client
    ini_location = options['ini']
    if not ini_location:
        raise Exception('You need to pass pyramid ini location using '
                        '--ini=filename.ini argument to the worker')
    env = bootstrap(ini_location)
    api_key = env['request'].registry.settings['appenlight.api_key']
    tr_config = env['request'].registry.settings.get(
        'appenlight.transport_config')
    CONFIG = e_client.get_config({'appenlight.api_key': api_key})
    if tr_config:
        CONFIG['appenlight.transport_config'] = tr_config
    APPENLIGHT_CLIENT = e_client.Client(CONFIG)
    # log.addHandler(APPENLIGHT_CLIENT.log_handler)
    register_signals(APPENLIGHT_CLIENT)
    celery.pyramid = env


celery_config = {
    'CELERY_IMPORTS': ["appenlight.celery.tasks", ],
    'CELERYD_TASK_TIME_LIMIT': 60,
    'CELERYD_MAX_TASKS_PER_CHILD': 1000,
    'CELERY_IGNORE_RESULT': True,
    'CELERY_ACCEPT_CONTENT': ['date_json'],
    'CELERY_TASK_SERIALIZER': 'date_json',
    'CELERY_RESULT_SERIALIZER': 'date_json',
    'BROKER_URL': None,
    'CELERYD_CONCURRENCY': None,
    'CELERY_TIMEZONE': None,
    'CELERYBEAT_SCHEDULE': {
        'alerting_reports': {
            'task': 'appenlight.celery.tasks.alerting_reports',
            'schedule': timedelta(seconds=60)
        },
        'close_alerts': {
            'task': 'appenlight.celery.tasks.close_alerts',
            'schedule': timedelta(seconds=60)
        }
    }
}
celery.config_from_object(celery_config)


def configure_celery(pyramid_registry):
    settings = pyramid_registry.settings
    celery_config['BROKER_URL'] = settings['celery.broker_url']
    celery_config['CELERYD_CONCURRENCY'] = settings['celery.concurrency']
    celery_config['CELERY_TIMEZONE'] = settings['celery.timezone']

    notifications_seconds = int(settings.get('tasks.notifications_reports.interval', 60))

    celery_config['CELERYBEAT_SCHEDULE']['notifications'] = {
        'task': 'appenlight.celery.tasks.notifications_reports',
        'schedule': timedelta(seconds=notifications_seconds)
    }

    celery_config['CELERYBEAT_SCHEDULE']['daily_digest'] = {
        'task': 'appenlight.celery.tasks.daily_digest',
        'schedule': crontab(minute=1, hour='4,12,20')
    }

    if asbool(settings.get('celery.always_eager')):
        celery_config['CELERY_ALWAYS_EAGER'] = True
        celery_config['CELERY_EAGER_PROPAGATES_EXCEPTIONS'] = True

    for plugin in pyramid_registry.appenlight_plugins.values():
        if plugin.get('celery_tasks'):
            celery_config['CELERY_IMPORTS'].extend(plugin['celery_tasks'])
        if plugin.get('celery_beats'):
            for name, config in plugin['celery_beats']:
                celery_config['CELERYBEAT_SCHEDULE'][name] = config
    celery.config_from_object(celery_config)


@task_prerun.connect
def task_prerun_signal(task_id, task, args, kwargs, **kwaargs):
    if hasattr(celery, 'pyramid'):
        env = celery.pyramid
        env = prepare(registry=env['request'].registry)
        proper_base_url = env['request'].registry.settings['mailing.app_url']
        tmp_req = Request.blank('/', base_url=proper_base_url)
        # ensure tasks generate url for right domain from config
        env['request'].environ['HTTP_HOST'] = tmp_req.environ['HTTP_HOST']
        env['request'].environ['SERVER_PORT'] = tmp_req.environ['SERVER_PORT']
        env['request'].environ['SERVER_NAME'] = tmp_req.environ['SERVER_NAME']
        env['request'].environ['wsgi.url_scheme'] = \
            tmp_req.environ['wsgi.url_scheme']
    get_current_request().tm.begin()


@task_success.connect
def task_success_signal(result, **kwargs):
    get_current_request().tm.commit()
    if hasattr(celery, 'pyramid'):
        celery.pyramid["closer"]()


@task_retry.connect
def task_retry_signal(request, reason, einfo, **kwargs):
    get_current_request().tm.abort()
    if hasattr(celery, 'pyramid'):
        celery.pyramid["closer"]()


@task_failure.connect
def task_failure_signal(task_id, exception, args, kwargs, traceback, einfo,
                        **kwaargs):
    get_current_request().tm.abort()
    if hasattr(celery, 'pyramid'):
        celery.pyramid["closer"]()


@task_revoked.connect
def task_revoked_signal(request, terminated, signum, expired, **kwaargs):
    get_current_request().tm.abort()
    if hasattr(celery, 'pyramid'):
        celery.pyramid["closer"]()
