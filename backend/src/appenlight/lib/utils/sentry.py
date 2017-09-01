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

from datetime import timedelta

from appenlight.lib.enums import LogLevelPython, ParsedSentryEventType

EXCLUDED_LOG_VARS = [
    'args', 'asctime', 'created', 'exc_info', 'exc_text', 'filename',
    'funcName', 'levelname', 'levelno', 'lineno', 'message', 'module', 'msecs',
    'msg', 'name', 'pathname', 'process', 'processName', 'relativeCreated',
    'thread', 'threadName']

EXCLUDE_SENTRY_KEYS = [
    'csp',
    'culprit',
    'event_id',
    'exception',
    'extra',
    'level',
    'logentry',
    'logger',
    'message',
    'modules',
    'platform',
    'query',
    'release',
    'request',
    'sentry.interfaces.Csp', 'sentry.interfaces.Exception',
    'sentry.interfaces.Http', 'sentry.interfaces.Message',
    'sentry.interfaces.Query',
    'sentry.interfaces.Stacktrace',
    'sentry.interfaces.Template', 'sentry.interfaces.User',
    'sentry.interfaces.csp.Csp',
    'sentry.interfaces.exception.Exception',
    'sentry.interfaces.http.Http',
    'sentry.interfaces.message.Message',
    'sentry.interfaces.query.Query',
    'sentry.interfaces.stacktrace.Stacktrace',
    'sentry.interfaces.template.Template',
    'sentry.interfaces.user.User', 'server_name',
    'stacktrace',
    'tags',
    'template',
    'time_spent',
    'timestamp',
    'user']


def get_keys(list_of_keys, json_body):
    for k in list_of_keys:
        if k in json_body:
            return json_body[k]


def get_logentry(json_body):
    key_names = ['logentry',
                 'sentry.interfaces.message.Message',
                 'sentry.interfaces.Message'
                 ]
    logentry = get_keys(key_names, json_body)
    return logentry


def get_exception(json_body):
    parsed_exception = {}
    key_names = ['exception',
                 'sentry.interfaces.exception.Exception',
                 'sentry.interfaces.Exception'
                 ]
    exception = get_keys(key_names, json_body) or {}
    if exception:
        if isinstance(exception, dict):
            exception = exception['values'][0]
        else:
            exception = exception[0]

    parsed_exception['type'] = exception.get('type')
    parsed_exception['value'] = exception.get('value')
    parsed_exception['module'] = exception.get('module')
    parsed_stacktrace = get_stacktrace(exception) or {}
    parsed_exception = exception or {}
    return parsed_exception, parsed_stacktrace


def get_stacktrace(json_body):
    parsed_stacktrace = []
    key_names = ['stacktrace',
                 'sentry.interfaces.stacktrace.Stacktrace',
                 'sentry.interfaces.Stacktrace'
                 ]
    stacktrace = get_keys(key_names, json_body)
    if stacktrace:
        for frame in stacktrace['frames']:
            parsed_stacktrace.append(
                {"cline": frame.get('context_line', ''),
                 "file": frame.get('filename', ''),
                 "module": frame.get('module', ''),
                 "fn": frame.get('function', ''),
                 "line": frame.get('lineno', ''),
                 "vars": list(frame.get('vars', {}).items())
                 }
            )
    return parsed_stacktrace


def get_template(json_body):
    parsed_template = {}
    key_names = ['template',
                 'sentry.interfaces.template.Template',
                 'sentry.interfaces.Template'
                 ]
    template = get_keys(key_names, json_body)
    if template:
        for frame in template['frames']:
            parsed_template.append(
                {"cline": frame.get('context_line', ''),
                 "file": frame.get('filename', ''),
                 "fn": '',
                 "line": frame.get('lineno', ''),
                 "vars": []
                 }
            )

    return parsed_template


def get_request(json_body):
    parsed_http = {}
    key_names = ['request',
                 'sentry.interfaces.http.Http',
                 'sentry.interfaces.Http'
                 ]
    http = get_keys(key_names, json_body) or {}
    for k, v in http.items():
        if k == 'headers':
            parsed_http['headers'] = {}
            for sk, sv in http['headers'].items():
                parsed_http['headers'][sk.title()] = sv
        else:
            parsed_http[k.lower()] = v
    return parsed_http


def get_user(json_body):
    parsed_user = {}
    key_names = ['user',
                 'sentry.interfaces.user.User',
                 'sentry.interfaces.User'
                 ]
    user = get_keys(key_names, json_body)
    if user:
        parsed_user['id'] = user.get('id')
        parsed_user['username'] = user.get('username')
        parsed_user['email'] = user.get('email')
        parsed_user['ip_address'] = user.get('ip_address')

    return parsed_user


def get_query(json_body):
    query = None
    key_name = ['query',
                'sentry.interfaces.query.Query',
                'sentry.interfaces.Query'
                ]
    query = get_keys(key_name, json_body)
    return query


def parse_sentry_event(json_body):
    request_id = json_body.get('event_id')

    # required
    message = json_body.get('message')
    log_timestamp = json_body.get('timestamp')
    level = json_body.get('level')
    if isinstance(level, int):
        level = LogLevelPython.key_from_value(level)

    namespace = json_body.get('logger')
    language = json_body.get('platform')

    # optional
    server_name = json_body.get('server_name')
    culprit = json_body.get('culprit')
    release = json_body.get('release')

    tags = json_body.get('tags', {})
    if hasattr(tags, 'items'):
        tags = list(tags.items())
    extra = json_body.get('extra', {})
    if hasattr(extra, 'items'):
        extra = list(extra.items())

    parsed_req = get_request(json_body)
    user = get_user(json_body)
    template = get_template(json_body)
    query = get_query(json_body)

    # other unidentified keys found
    other_keys = [(k, json_body[k]) for k in json_body.keys()
                  if k not in EXCLUDE_SENTRY_KEYS]

    logentry = get_logentry(json_body)
    if logentry:
        message = logentry['message']

    exception, stacktrace = get_exception(json_body)

    alt_stacktrace = get_stacktrace(json_body)
    event_type = None
    if not exception and not stacktrace and not alt_stacktrace and not template:
        event_type = ParsedSentryEventType.LOG

        event_dict = {
            'log_level': level,
            'message': message,
            'namespace': namespace,
            'request_id': request_id,
            'server': server_name,
            'date': log_timestamp,
            'tags': tags
        }
        event_dict['tags'].extend(
            [(k, v) for k, v in extra if k not in EXCLUDED_LOG_VARS])

        # other keys can be various object types
        event_dict['tags'].extend([(k, v) for k, v in other_keys
                                   if isinstance(v, str)])
        if culprit:
            event_dict['tags'].append(('sentry_culprit', culprit))
        if language:
            event_dict['tags'].append(('sentry_language', language))
        if release:
            event_dict['tags'].append(('sentry_release', release))

    if exception or stacktrace or alt_stacktrace or template:
        event_type = ParsedSentryEventType.ERROR_REPORT
        event_dict = {
            'client': 'sentry',
            'error': message,
            'namespace': namespace,
            'request_id': request_id,
            'server': server_name,
            'start_time': log_timestamp,
            'end_time': None,
            'tags': tags,
            'extra': extra,
            'language': language,
            'view_name': json_body.get('culprit'),
            'http_status': None,
            'username': None,
            'url': parsed_req.get('url'),
            'ip': None,
            'user_agent': None,
            'request': None,
            'slow_calls': None,
            'request_stats': None,
            'traceback': None
        }

        event_dict['extra'].extend(other_keys)
        if release:
            event_dict['tags'].append(('sentry_release', release))
        event_dict['request'] = parsed_req
        if 'headers' in parsed_req:
            event_dict['user_agent'] = parsed_req['headers'].get('User-Agent')
        if 'env' in parsed_req:
            event_dict['ip'] = parsed_req['env'].get('REMOTE_ADDR')
        ts_ms = int(json_body.get('time_spent') or 0)
        if ts_ms > 0:
            event_dict['end_time'] = event_dict['start_time'] + \
                                     timedelta(milliseconds=ts_ms)
        if stacktrace or alt_stacktrace or template:
            event_dict['traceback'] = stacktrace or alt_stacktrace or template
        for k in list(event_dict.keys()):
            if event_dict[k] is None:
                del event_dict[k]
        if user:
            event_dict['username'] = user['username'] or user['id'] \
                                     or user['email']
    return event_dict, event_type
