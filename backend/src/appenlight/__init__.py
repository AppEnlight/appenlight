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

import datetime
import logging
from elasticsearch import Elasticsearch
import redis
import os
import pkg_resources
from pkg_resources import iter_entry_points

import appenlight.lib.jinja2_filters as jinja2_filters
import appenlight.lib.encryption as encryption

from pyramid.config import PHASE3_CONFIG
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid_mailer.interfaces import IMailer
from pyramid.renderers import JSON
from pyramid_redis_sessions import session_factory_from_settings
from pyramid.settings import asbool, aslist
from pyramid.security import AllPermissionsList
from pyramid_authstack import AuthenticationStackPolicy
from redlock import Redlock
from sqlalchemy import engine_from_config

from appenlight.celery import configure_celery
from appenlight.lib.configurator import (CythonCompatConfigurator,
                                         register_appenlight_plugin)
from appenlight.lib import cache_regions
from appenlight.lib.ext_json import json
from appenlight.security import groupfinder, AuthTokenAuthenticationPolicy

__license__ = 'Apache 2.0'
__author__ = 'RhodeCode GmbH'
__url__ = 'http://rhodecode.com'
__version__ = pkg_resources.get_distribution("appenlight").parsed_version

json_renderer = JSON(serializer=json.dumps, indent=4)

log = logging.getLogger(__name__)


def datetime_adapter(obj, request):
    return obj.isoformat()


def all_permissions_adapter(obj, request):
    return '__all_permissions__'


json_renderer.add_adapter(datetime.datetime, datetime_adapter)
json_renderer.add_adapter(AllPermissionsList, all_permissions_adapter)


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    auth_tkt_policy = AuthTktAuthenticationPolicy(
        settings['authtkt.secret'],
        hashalg='sha512',
        callback=groupfinder,
        max_age=2592000,
        secure=asbool(settings.get('authtkt.secure', 'false')))
    auth_token_policy = AuthTokenAuthenticationPolicy(
        callback=groupfinder
    )
    authorization_policy = ACLAuthorizationPolicy()
    authentication_policy = AuthenticationStackPolicy()
    authentication_policy.add_policy('auth_tkt', auth_tkt_policy)
    authentication_policy.add_policy('auth_token', auth_token_policy)
    # set crypto key
    encryption.ENCRYPTION_SECRET = settings.get('encryption_secret')
    # import this later so encyption key can be monkeypatched
    from appenlight.models import DBSession, register_datastores

    # registration
    settings['appenlight.disable_registration'] = asbool(
        settings.get('appenlight.disable_registration'))

    # update config with cometd info
    settings['cometd_servers'] = {'server': settings['cometd.server'],
                                  'secret': settings['cometd.secret']}

    # Create the Pyramid Configurator.
    settings['_mail_url'] = settings['mailing.app_url']
    config = CythonCompatConfigurator(
        settings=settings,
        authentication_policy=authentication_policy,
        authorization_policy=authorization_policy,
        root_factory='appenlight.security.RootFactory',
        default_permission='view')
    # custom registry variables

    # resource type information
    config.registry.resource_types = ['resource', 'application']
    # plugin information
    config.registry.appenlight_plugins = {}

    config.set_default_csrf_options(require_csrf=True, header='X-XSRF-TOKEN')
    config.add_view_deriver('appenlight.predicates.csrf_view',
                            name='csrf_view')

    # later, when config is available
    dogpile_config = {'url': settings['redis.url'],
                      "redis_expiration_time": 86400,
                      "redis_distributed_lock": True}
    cache_regions.regions = cache_regions.CacheRegions(dogpile_config)
    config.registry.cache_regions = cache_regions.regions
    engine = engine_from_config(settings, 'sqlalchemy.',
                                json_serializer=json.dumps)
    DBSession.configure(bind=engine)

    # json rederer that serializes datetime
    config.add_renderer('json', json_renderer)
    config.add_request_method('appenlight.lib.request.es_conn', 'es_conn', property=True)
    config.add_request_method('appenlight.lib.request.get_user', 'user',
                                reify=True, property=True)
    config.add_request_method('appenlight.lib.request.get_csrf_token',
                                'csrf_token', reify=True, property=True)
    config.add_request_method('appenlight.lib.request.safe_json_body',
                                'safe_json_body', reify=True, property=True)
    config.add_request_method('appenlight.lib.request.unsafe_json_body',
                                'unsafe_json_body', reify=True, property=True)
    config.add_request_method('appenlight.lib.request.add_flash_to_headers',
                              'add_flash_to_headers')
    config.add_request_method('appenlight.lib.request.get_authomatic',
                              'authomatic', reify=True)

    config.include('pyramid_redis_sessions')
    config.include('pyramid_tm')
    config.include('pyramid_jinja2')
    config.include('pyramid_mailer')
    config.include('appenlight_client.ext.pyramid_tween')
    config.include('ziggurat_foundations.ext.pyramid.sign_in')
    es_server_list = aslist(settings['elasticsearch.nodes'])
    redis_url = settings['redis.url']
    log.warning('Elasticsearch server list: {}'.format(es_server_list))
    log.warning('Redis server: {}'.format(redis_url))
    config.registry.es_conn = Elasticsearch(es_server_list)
    config.registry.redis_conn = redis.StrictRedis.from_url(redis_url)

    config.registry.redis_lockmgr = Redlock([settings['redis.redlock.url'], ],
                                            retry_count=0, retry_delay=0)
    # mailer bw compat
    config.registry.mailer = config.registry.getUtility(IMailer)

    # Configure sessions
    session_factory = session_factory_from_settings(settings)
    config.set_session_factory(session_factory)

    # Configure renderers and event subscribers
    config.add_jinja2_extension('jinja2.ext.loopcontrols')
    config.add_jinja2_search_path('appenlight:templates')
    # event subscribers
    config.add_subscriber("appenlight.subscribers.application_created",
                          "pyramid.events.ApplicationCreated")
    config.add_subscriber("appenlight.subscribers.add_renderer_globals",
                          "pyramid.events.BeforeRender")
    config.add_subscriber('appenlight.subscribers.new_request',
                          'pyramid.events.NewRequest')
    config.add_view_predicate('context_type_class',
                              'appenlight.predicates.contextTypeClass')

    register_datastores(es_conn=config.registry.es_conn,
                        redis_conn=config.registry.redis_conn,
                        redis_lockmgr=config.registry.redis_lockmgr)

    # base stuff and scan

    # need to ensure webassets exists otherwise config.override_asset()
    # throws exception
    if not os.path.exists(settings['webassets.dir']):
        os.mkdir(settings['webassets.dir'])
    config.add_static_view(path='appenlight:webassets',
                           name='static', cache_max_age=3600)
    config.override_asset(to_override='appenlight:webassets/',
                          override_with=settings['webassets.dir'])

    config.include('appenlight.views')
    config.include('appenlight.views.admin')
    config.scan(ignore=['appenlight.migrations', 'appenlight.scripts',
                        'appenlight.tests'])

    config.add_directive('register_appenlight_plugin',
                         register_appenlight_plugin)

    for entry_point in iter_entry_points(group='appenlight.plugins'):
        plugin = entry_point.load()
        plugin.includeme(config)

    # include other appenlight plugins explictly if needed
    includes = aslist(settings.get('appenlight.includes', []))
    for inc in includes:
        config.include(inc)

    # run this after everything registers in configurator

    def pre_commit():
        jinja_env = config.get_jinja2_environment()
        jinja_env.filters['tojson'] = json.dumps
        jinja_env.filters['toJSONUnsafe'] = jinja2_filters.toJSONUnsafe

    config.action(None, pre_commit, order=PHASE3_CONFIG + 999)

    def wrap_config_celery():
        configure_celery(config.registry)

    config.action(None, wrap_config_celery, order=PHASE3_CONFIG + 999)

    app = config.make_wsgi_app()
    return app
