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

"""View handlers package.
"""
from pyramid.response import Response
import logging
import simplejson as json
from appenlight.lib import helpers

log = logging.getLogger(__name__)


def includeme(config):
    """Add the application's view handlers.
    """

    config.add_route('/', '/')
    config.add_route('angular_app_ui_ix', '/ui')
    config.add_route('angular_app_ui', '/ui/*remainder')

    # applications API
    config.add_route('applications_no_id', '/applications')
    config.add_route('applications', '/applications/{resource_id}',
                     factory='appenlight.security.ResourceFactory')
    config.add_route('applications_property',
                     '/applications/{resource_id}/{key}',
                     factory='appenlight.security.ResourceFactory')
    config.add_route(
        'integrations_id',
        '/applications/{resource_id}/integrations/{integration}/{action}',
        factory='appenlight.security.ResourceFactory')

    # users API
    config.add_route('users_self', '/users/self')
    config.add_route('users_self_property', '/users/self/{key}')
    config.add_route('users_no_id', '/users')
    config.add_route('users', '/users/{user_id}')
    config.add_route('users_property', '/users/{user_id}/{key}')

    # events
    config.add_route('events_no_id', '/events')
    config.add_route('events', '/events/{event_id}')
    config.add_route('events_property', '/events/{event_id}/{key}')

    # groups
    config.add_route('groups_no_id', '/groups')
    config.add_route('groups', '/groups/{group_id}')
    config.add_route('groups_property', '/groups/{group_id}/{key}')

    # reports API
    config.add_route('reports', '/reports')
    config.add_route('slow_reports', '/slow_reports')
    config.add_route('report_groups', '/report_groups/{group_id}',
                     factory='appenlight.security.ResourceReportFactory')
    config.add_route('report_groups_property',
                     '/report_groups/{group_id}/{key}',
                     factory='appenlight.security.ResourceReportFactory')

    #generic resource API
    config.add_route('resources_property',
                     '/resources/{resource_id}/{key}',
                     factory='appenlight.security.ResourceFactory')

    # plugin configs API
    config.add_route('plugin_configs', '/plugin_configs/{plugin_name}',
                     factory='appenlight.security.ResourcePluginMixedFactory')
    config.add_route('plugin_config', '/plugin_configs/{plugin_name}/{id}',
                     factory='appenlight.security.ResourcePluginConfigFactory')

    # client endpoints API
    config.add_route('api_reports', '/api/reports',
                     factory='appenlight.security.APIFactory')
    config.add_route('api_report', '/api/report',
                     factory='appenlight.security.APIFactory')
    config.add_route('api_logs', '/api/logs',
                     factory='appenlight.security.APIFactory')
    config.add_route('api_log', '/api/log',
                     factory='appenlight.security.APIFactory')
    config.add_route('api_slow_reports', '/api/slow_reports',
                     factory='appenlight.security.APIFactory')
    config.add_route('api_request_stats', '/api/request_stats',
                     factory='appenlight.security.APIFactory')
    config.add_route('api_metrics', '/api/metrics',
                     factory='appenlight.security.APIFactory')
    config.add_route('api_general_metrics', '/api/general_metrics',
                     factory='appenlight.security.APIFactory')
    config.add_route('api_general_metric', '/api/general_metric',
                     factory='appenlight.security.APIFactory')
    config.add_route('api_airbrake', '/notifier_api/v2/{action}',
                     factory='appenlight.security.AirbrakeV2APIFactory')
    config.add_route('api_sentry', '/api/{project}/store',
                     factory='appenlight.security.SentryAPIFactory')
    config.add_route('api_sentry_slash', '/api/{project}/store/',
                     factory='appenlight.security.SentryAPIFactory')

    # other
    config.add_route('register', '/register')
    config.add_route('register_ajax', '/register_ajax')
    config.add_route('lost_password', '/lost_password')
    config.add_route('lost_password_generate', '/lost_password_generate')
    config.add_route('logs_no_id', '/logs')
    config.add_route('forbidden', '/forbidden')
    config.add_route('test', '/test/{action}')
    config.add_route('section_view', '/sections/{section}/{view}')

    config.add_view('appenlight.views.forbidden_view',
                    context='pyramid.exceptions.Forbidden',
                    renderer='appenlight:templates/forbidden.jinja2',
                    permission='__no_permission_required__')
    config.add_view('appenlight.views.not_found_view',
                    context='pyramid.exceptions.NotFound',
                    renderer='appenlight:templates/not_found.jinja2',
                    permission='__no_permission_required__')
    config.add_view('appenlight.views.csrf_view',
                    context='appenlight.lib.request.CSRFException',
                    renderer='appenlight:templates/forbidden.jinja2',
                    permission='__no_permission_required__')
    config.add_view('appenlight.views.csrf_view',
                    context='appenlight.forms.CSRFException',
                    renderer='appenlight:templates/forbidden.jinja2',
                    permission='__no_permission_required__')
    config.add_view('appenlight.views.colander_invalid_view',
                    context='colander.Invalid',
                    renderer='json',
                    permission='__no_permission_required__')
    config.add_view('appenlight.views.bad_json_view',
                    context='appenlight.lib.request.JSONException',
                    renderer='json',
                    permission='__no_permission_required__')

    # handle authomatic
    config.add_route('social_auth', '/social_auth/{provider}')
    config.add_route('social_auth_abort', '/social_auth/{provider}/abort')

    # only use in production
    if (config.registry.settings.get('pyramid.reload_templates') is False
        and config.registry.settings.get('pyramid.debug_templates') is False):
        config.add_view('appenlight.views.error_view',
                        context=Exception,
                        renderer='appenlight:templates/error.jinja2',
                        permission='__no_permission_required__')


def bad_json_view(exc, request):
    request.environ['appenlight.ignore_error'] = 1
    request.response.headers.add('X-AppEnlight-Error', 'Incorrect JSON')
    request.response.status_int = 400
    return "Incorrect JSON"


def colander_invalid_view(exc, request):
    request.environ['appenlight.ignore_error'] = 1
    log.warning('API version %s, %s' % (
        request.params.get('protocol_version'),
        request.context.resource))
    log.warning('Invalid payload sent')
    errors = exc.asdict()
    request.response.headers.add('X-AppEnlight-Error', 'Invalid payload sent')
    request.response.status_int = 422
    return errors


def csrf_view(exc, request):
    request.response.status = 403
    from ..models import DBSession
    request.environ["appenlight.ignore_error"] = 1
    request.response.headers.add('X-AppEnlight-Error', str(exc))
    if request.user:
        request.user = DBSession.merge(request.user)
    return {'forbidden_view': True, 'csrf': True}


def not_found_view(exc, request):
    request.response.status = 404
    from ..models import DBSession

    if request.user:
        request.user = DBSession.merge(request.user)

    if request.user:
        request.response.headers['x-appenlight-uid'] = '%s' % request.user.id
    request.response.headers['x-appenlight-flash'] = json.dumps(
        helpers.get_flash(request))

    return {}


def forbidden_view(exc, request):
    # dont serve html for api requests
    from ..models import DBSession

    if request.user:
        request.user = DBSession.merge(request.user)
    if request.path.startswith('/api'):
        logging.warning('Wrong API Key sent')
        logging.info(request.url)
        logging.info(
            '\n'.join(
                ['%s:%s' % (k, v) for k, v in request.headers.items()]))
        resp = Response(
            "Wrong api key",
            headers=(('X-AppEnlight-Error', 'Incorrect API key',),))
        resp.status_int = 403
        return resp

    if request.user:
        request.response.headers['x-appenlight-uid'] = '%s' % request.user.id
    request.response.headers['x-appenlight-flash'] = json.dumps(
        helpers.get_flash(request))
    request.response.status = 403
    return {'forbidden_view': True}


def error_view(exc, request):
    from ..models import DBSession
    if request.user:
        request.user = DBSession.merge(request.user)
    if request.path.startswith('/api'):
        resp = Response(
            "There was a problem handling your request please try again",
            headers=(('X-AppEnlight-Error', 'Problem handling request',),)
        )
        resp.status_int = 500
        return resp
    log.error(exc)
    request.response.status = 500
    return {}
