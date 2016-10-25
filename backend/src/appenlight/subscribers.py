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

import hashlib
import os

from pyramid.i18n import TranslationStringFactory
from pyramid import threadlocal

_ = TranslationStringFactory('pyramid')

from appenlight import security
from appenlight.lib import helpers, generate_random_string
from appenlight.models.services.config import ConfigService


def gen_urls(request):
    urls = {
        'baseUrl': request.route_url('/'),
        'applicationsNoId': request.route_url('applications_no_id'),
        'applications': request.route_url('applications', resource_id='REPLACE_ID').replace('REPLACE_ID',':resourceId'),
        'applicationsProperty': request.route_url('applications_property',key='REPLACE_KEY', resource_id='REPLACE_ID').replace('REPLACE_ID',':resourceId').replace('REPLACE_KEY',':key'),
        'configsNoId': request.route_url('admin_configs'),
        'configs': request.route_url('admin_config', key='REPLACE_KEY', section='REPLACE_SECTION').replace('REPLACE_SECTION',':section').replace('REPLACE_KEY',':key'),
        'docs': 'http://getappenlight.com/page/api/main.html',
        'eventsNoId': request.route_url('events_no_id'),
        'events': request.route_url('events', event_id='REPLACE_ID').replace('REPLACE_ID',':eventId'),
        'eventsProperty': request.route_url('events_property',key='REPLACE_KEY', event_id='REPLACE_ID').replace('REPLACE_ID',':eventId').replace('REPLACE_KEY',':key'),
        'groupsNoId': request.route_url('groups_no_id'),
        'groups': request.route_url('groups', group_id='REPLACE_ID').replace('REPLACE_ID',':groupId'),
        'groupsProperty': request.route_url('groups_property',key='REPLACE_KEY', group_id='REPLACE_ID').replace('REPLACE_ID',':groupId').replace('REPLACE_KEY',':key'),
        'logsNoId': request.route_url('logs_no_id'),
        'integrationAction': request.route_url('integrations_id',action='REPLACE_ACT', resource_id='REPLACE_RID', integration='REPLACE_IID').replace('REPLACE_RID',':resourceId').replace('REPLACE_ACT',':action').replace('REPLACE_IID',':integration'),
        'usersNoId': request.route_url('users_no_id'),
        'users': request.route_url('users', user_id='REPLACE_ID').replace('REPLACE_ID',':userId'),
        'usersProperty': request.route_url('users_property',key='REPLACE_KEY', user_id='REPLACE_ID').replace('REPLACE_ID',':userId').replace('REPLACE_KEY',':key'),
        'userSelf': request.route_url('users_self'),
        'userSelfProperty': request.route_url('users_self_property',key='REPLACE_KEY').replace('REPLACE_KEY',':key'),
        'reports': request.route_url('reports'),
        'reportGroup': request.route_url('report_groups', group_id='REPLACE_RID').replace('REPLACE_RID',':groupId'),
        'reportGroupProperty': request.route_url('report_groups_property', key='REPLACE_KEY', group_id='REPLACE_GID').replace('REPLACE_KEY',':key').replace('REPLACE_GID',':groupId'),
        'pluginConfigsNoId': request.route_url('plugin_configs', plugin_name='REPLACE_TYPE').replace('REPLACE_TYPE',':plugin_name'),
        'pluginConfigs': request.route_url('plugin_config', id='REPLACE_ID', plugin_name='REPLACE_TYPE').replace('REPLACE_ID',':id').replace('REPLACE_TYPE',':plugin_name'),
        'resourceProperty': request.route_url('resources_property',key='REPLACE_KEY', resource_id='REPLACE_ID').replace('REPLACE_ID',':resourceId').replace('REPLACE_KEY',':key'),
        'slowReports': request.route_url('slow_reports'),
        'sectionView': request.route_url('section_view', section='REPLACE_S', view='REPLACE_V').replace('REPLACE_S',':section').replace('REPLACE_V',':view'),
        'otherRoutes': {
            'register': request.route_url('register'),
            'lostPassword': request.route_url('lost_password'),
            'lostPasswordGenerate': request.route_url('lost_password_generate'),
            'signOut': request.route_url('ziggurat.routes.sign_out')
        },
        'social_auth': {
            'google': request.route_url('social_auth', provider='google'),
            'twitter': request.route_url('social_auth', provider='twitter'),
            'bitbucket': request.route_url('social_auth', provider='bitbucket'),
            'github': request.route_url('social_auth', provider='github'),
        },
        "plugins": {},
        "adminAction": request.route_url('admin', action="REPLACE_ACT").replace('REPLACE_ACT',':action')
    }
    return urls

def new_request(event):
    environ = event.request.environ
    event.request.response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    event.request.response.headers['X-XSS-Protection'] = '1; mode=block'
    # can this be enabled on non https deployments?
    # event.request.response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubdomains;'

    # do not send XSRF token with /api calls
    if not event.request.path.startswith('/api'):
        if environ['wsgi.url_scheme'] == 'https':
            event.request.response.set_cookie(
                'XSRF-TOKEN', event.request.session.get_csrf_token(),
                secure=True)
        else:
            event.request.response.set_cookie(
                'XSRF-TOKEN', event.request.session.get_csrf_token())
    if event.request.user:
        event.request.response.headers[
            'x-appenlight-uid'] = '%s' % event.request.user.id


def add_renderer_globals(event):
    request = event.get("request") or threadlocal.get_current_request()

    renderer_globals = event
    renderer_globals["h"] = helpers
    renderer_globals["js_hash"] = request.registry.js_hash
    renderer_globals["css_hash"] = request.registry.css_hash
    renderer_globals['_'] = _
    renderer_globals['security'] = security
    renderer_globals['flash_msgs'] = []
    renderer_globals['appenlight_plugins'] = []

    if 'jinja' in event['renderer_info'].type:
        renderer_globals['url_list'] = gen_urls(request)
        # add footer html and some other global vars to renderer
        for module, config in request.registry.appenlight_plugins.items():
            if config['url_gen']:
                urls = config['url_gen'](request)
                renderer_globals['url_list']['plugins'][module] = urls

            renderer_globals['appenlight_plugins'].append(
                {'name': module,
                 'config': {
                     'javascript':config['javascript'],
                     'header_html':config['header_html']
                 }})

        footer_config = ConfigService.by_key_and_section(
            'template_footer_html', 'global', default_value='')

        renderer_globals['template_footer_html'] = footer_config.value
        try:
            renderer_globals['root_administrator'] = request.has_permission(
                'root_administration', security.RootFactory(request))
        except AttributeError:
            renderer_globals['root_administrator'] = False

    renderer_globals['_mail_url'] = request.registry.settings['_mail_url']

    if not request:
        return

    # do not sens flash headers with /api calls
    if not request.path.startswith('/api'):
        flash_msgs = helpers.get_type_formatted_flash(request)
        renderer_globals['flash_msgs'] = flash_msgs
        request.add_flash_to_headers()

def application_created(app):
    webassets_dir = app.app.registry.settings.get('webassets.dir')
    js_hash = generate_random_string()
    css_hash = generate_random_string()
    if webassets_dir:
        js_hasher = hashlib.md5()
        css_hasher = hashlib.md5()
        for root, dirs, files in os.walk(webassets_dir):
            for name in files:
                filename = os.path.join(root, name)
                if name.endswith('css'):
                    with open(filename, 'r', encoding='utf8',
                              errors='replace') as f:
                        for line in f:
                            css_hasher.update(line.encode('utf8'))
                elif name.endswith('js'):
                    with open(filename, 'r', encoding='utf8',
                              errors='replace') as f:
                        for line in f:
                            js_hasher.update(line.encode('utf8'))
        js_hash = js_hasher.hexdigest()
        css_hash = css_hasher.hexdigest()
    app.app.registry.js_hash = js_hash
    app.app.registry.css_hash = css_hash
