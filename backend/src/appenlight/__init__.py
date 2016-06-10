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

import datetime
import logging
import pyelasticsearch
import redis
import os
from pkg_resources import iter_entry_points

import appenlight.lib.jinja2_filters as jinja2_filters
import appenlight.lib.encryption as encryption

from authomatic.providers import oauth2, oauth1
from authomatic import Authomatic
from pyramid.config import Configurator, PHASE3_CONFIG
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid_mailer.mailer import Mailer
from pyramid.renderers import JSON
from pyramid_redis_sessions import session_factory_from_settings
from pyramid.settings import asbool, aslist
from pyramid.security import AllPermissionsList
from pyramid_authstack import AuthenticationStackPolicy
from redlock import Redlock
from sqlalchemy import engine_from_config

from appenlight.celery import configure_celery
from appenlight.lib import cache_regions
from appenlight.lib.ext_json import json
from appenlight.security import groupfinder, AuthTokenAuthenticationPolicy

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
    # update config with cometd info
    settings['cometd_servers'] = {'server': settings['cometd.server'],
                                  'secret': settings['cometd.secret']}

    # Create the Pyramid Configurator.
    settings['_mail_url'] = settings['mailing.app_url']
    config = Configurator(settings=settings,
                          authentication_policy=authentication_policy,
                          authorization_policy=authorization_policy,
                          root_factory='appenlight.security.RootFactory',
                          default_permission='view')
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
    config.set_request_property('appenlight.lib.request.es_conn', 'es_conn')
    config.set_request_property('appenlight.lib.request.get_user', 'user',
                                reify=True)
    config.set_request_property('appenlight.lib.request.get_csrf_token',
                                'csrf_token', reify=True)
    config.set_request_property('appenlight.lib.request.safe_json_body',
                                'safe_json_body', reify=True)
    config.set_request_property('appenlight.lib.request.unsafe_json_body',
                                'unsafe_json_body', reify=True)
    config.add_request_method('appenlight.lib.request.add_flash_to_headers',
                              'add_flash_to_headers')

    config.include('pyramid_redis_sessions')
    config.include('pyramid_tm')
    config.include('pyramid_jinja2')
    config.include('appenlight_client.ext.pyramid_tween')
    config.include('ziggurat_foundations.ext.pyramid.sign_in')
    es_server_list = aslist(settings['elasticsearch.nodes'])
    redis_url = settings['redis.url']
    log.info('Elasticsearch server list: {}'.format(es_server_list))
    log.info('Redis server: {}'.format(redis_url))
    config.registry.es_conn = pyelasticsearch.ElasticSearch(es_server_list)
    config.registry.redis_conn = redis.StrictRedis.from_url(redis_url)

    config.registry.redis_lockmgr = Redlock([settings['redis.redlock.url'], ],
                                            retry_count=0, retry_delay=0)
    # mailer
    config.registry.mailer = Mailer.from_settings(settings)

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
    config.scan(ignore=['appenlight.migrations',
                        'appenlight.scripts',
                        'appenlight.tests'])

    # authomatic social auth
    authomatic_conf = {
        # callback http://yourapp.com/social_auth/twitter
        'twitter': {
            'class_': oauth1.Twitter,
            'consumer_key': settings.get('authomatic.pr.twitter.key', 'X'),
            'consumer_secret': settings.get('authomatic.pr.twitter.secret',
                                            'X'),
        },
        # callback http://yourapp.com/social_auth/facebook
        'facebook': {
            'class_': oauth2.Facebook,
            'consumer_key': settings.get('authomatic.pr.facebook.app_id', 'X'),
            'consumer_secret': settings.get('authomatic.pr.facebook.secret',
                                            'X'),
            'scope': ['email'],
        },
        # callback http://yourapp.com/social_auth/google
        'google': {
            'class_': oauth2.Google,
            'consumer_key': settings.get('authomatic.pr.google.key', 'X'),
            'consumer_secret': settings.get(
                'authomatic.pr.google.secret', 'X'),
            'scope': ['profile', 'email'],
        },
        'github': {
            'class_': oauth2.GitHub,
            'consumer_key': settings.get('authomatic.pr.github.key', 'X'),
            'consumer_secret': settings.get(
                'authomatic.pr.github.secret', 'X'),
            'scope': ['repo', 'public_repo', 'user:email'],
            'access_headers': {'User-Agent': 'AppEnlight'},
        },
        'bitbucket': {
            'class_': oauth1.Bitbucket,
            'consumer_key': settings.get('authomatic.pr.bitbucket.key', 'X'),
            'consumer_secret': settings.get(
                'authomatic.pr.bitbucket.secret', 'X')
        }
    }
    config.registry.authomatic = Authomatic(
        config=authomatic_conf, secret=settings['authomatic.secret'])

    # resource type information
    config.registry.resource_types = ['resource', 'application']

    # plugin information
    config.registry.appenlight_plugins = {}

    def register_appenlight_plugin(config, plugin_name, plugin_config):
        def register():
            log.warning('Registering plugin: {}'.format(plugin_name))
            if plugin_name not in config.registry.appenlight_plugins:
                config.registry.appenlight_plugins[plugin_name] = {
                    'javascript': None,
                    'static': None,
                    'css': None,
                    'top_nav': None,
                    'celery_tasks': None,
                    'celery_beats': None,
                    'fulltext_indexer': None,
                    'sqlalchemy_migrations': None,
                    'default_values_setter': None,
                    'resource_types': [],
                    'url_gen': None
                }
            config.registry.appenlight_plugins[plugin_name].update(
                plugin_config)
            # inform AE what kind of resource types we have available
            # so we can avoid failing when a plugin is removed but data
            # is still present in the db
            if plugin_config.get('resource_types'):
                config.registry.resource_types.extend(
                    plugin_config['resource_types'])

        config.action('appenlight_plugin={}'.format(plugin_name), register)

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
