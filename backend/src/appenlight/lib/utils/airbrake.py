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
import uuid

from datetime import datetime

log = logging.getLogger(__name__)


def parse_airbrake_xml(request):
    root = request.context.airbrake_xml_etree
    error = root.find('error')
    notifier = root.find('notifier')
    server_env = root.find('server-environment')
    request_data = root.find('request')
    user = root.find('current-user')
    if request_data is not None:
        cgi_data = request_data.find('cgi-data')
        if cgi_data is None:
            cgi_data = []

    error_dict = {
        'class_name': error.findtext('class') or '',
        'error': error.findtext('message') or '',
        "occurences": 1,
        "http_status": 500,
        "priority": 5,
        "server": 'unknown',
        'url': 'unknown', 'request': {}
    }
    if user is not None:
        error_dict['username'] = user.findtext('username') or \
                                 user.findtext('id')
    if notifier is not None:
        error_dict['client'] = notifier.findtext('name')

    if server_env is not None:
        error_dict["server"] = server_env.findtext('hostname', 'unknown')

    whitelist_environ = ['REMOTE_USER', 'REMOTE_ADDR', 'SERVER_NAME',
                         'CONTENT_TYPE', 'HTTP_REFERER']

    if request_data is not None:
        error_dict['url'] = request_data.findtext('url', 'unknown')
        component = request_data.findtext('component')
        action = request_data.findtext('action')
        if component and action:
            error_dict['view_name'] = '%s:%s' % (component, action)
        for node in cgi_data:
            key = node.get('key')
            if key.startswith('HTTP') or key in whitelist_environ:
                error_dict['request'][key] = node.text
            elif 'query_parameters' in key:
                error_dict['request']['GET'] = {}
                for x in node:
                    error_dict['request']['GET'][x.get('key')] = x.text
            elif 'request_parameters' in key:
                error_dict['request']['POST'] = {}
                for x in node:
                    error_dict['request']['POST'][x.get('key')] = x.text
            elif key.endswith('cookie'):
                error_dict['request']['COOKIE'] = {}
                for x in node:
                    error_dict['request']['COOKIE'][x.get('key')] = x.text
            elif key.endswith('request_id'):
                error_dict['request_id'] = node.text
            elif key.endswith('session'):
                error_dict['request']['SESSION'] = {}
                for x in node:
                    error_dict['request']['SESSION'][x.get('key')] = x.text
            else:
                if key in ['rack.session.options']:
                    # skip secret configs
                    continue
                try:
                    if len(node):
                        error_dict['request'][key] = dict(
                            [(x.get('key'), x.text,) for x in node])
                    else:
                        error_dict['request'][key] = node.text
                except Exception as e:
                    log.warning('Airbrake integration exception: %s' % e)

            error_dict['request'].pop('HTTP_COOKIE', '')

        error_dict['ip'] = error_dict.pop('REMOTE_ADDR', '')
        error_dict['user_agent'] = error_dict.pop('HTTP_USER_AGENT', '')
    if 'request_id' not in error_dict:
        error_dict['request_id'] = str(uuid.uuid4())
    if request.context.possibly_public:
        # set ip for reports that come from airbrake js client
        error_dict["timestamp"] = datetime.utcnow()
        if request.environ.get("HTTP_X_FORWARDED_FOR"):
            ip = request.environ.get("HTTP_X_FORWARDED_FOR", '')
            first_ip = ip.split(',')[0]
            remote_addr = first_ip.strip()
        else:
            remote_addr = (request.environ.get("HTTP_X_REAL_IP") or
                           request.environ.get('REMOTE_ADDR'))
        error_dict["ip"] = remote_addr

    blacklist = ['password', 'passwd', 'pwd', 'auth_tkt', 'secret', 'csrf',
                 'session', 'test']

    lines = []
    for l in error.find('backtrace'):
        lines.append({'file': l.get("file", ""),
                      'line': l.get("number", ""),
                      'fn': l.get("method", ""),
                      'module': l.get("module", ""),
                      'cline': l.get("method", ""),
                      'vars': {}})
    error_dict['traceback'] = list(reversed(lines))
    # filtering is not provided by airbrake
    keys_to_check = (
        error_dict['request'].get('COOKIE'),
        error_dict['request'].get('COOKIES'),
        error_dict['request'].get('POST'),
        error_dict['request'].get('SESSION'),
    )
    for source in [_f for _f in keys_to_check if _f]:
        for k in source.keys():
            for bad_key in blacklist:
                if bad_key in k.lower():
                    source[k] = '***'

    return error_dict
