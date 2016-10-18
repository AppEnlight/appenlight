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

import copy
import logging
import mock
import pyramid
import pytest
import sqlalchemy as sa
import webob

from datetime import datetime
from pyramid import testing


from appenlight.models import DBSession
from appenlight.lib.ext_json import json


log = logging.getLogger(__name__)


class DummyContext(object):
    pass


@pytest.mark.usefixtures('base_app')
class BasicTest(object):
    pass


@pytest.mark.usefixtures('base_app')
class TestMigration(object):
    def test_migration(self):
        assert 1 == 1


class TestSentryProto_7(object):
    def test_log_payload(self):
        import appenlight.tests.payload_examples as payload_examples
        from appenlight.lib.enums import ParsedSentryEventType
        from appenlight.lib.utils.sentry import parse_sentry_event
        event_dict, event_type = parse_sentry_event(
            payload_examples.SENTRY_LOG_PAYLOAD_7)
        assert ParsedSentryEventType.LOG == event_type
        assert event_dict['log_level'] == 'CRITICAL'
        assert event_dict['message'] == 'TEST from django logging'
        assert event_dict['namespace'] == 'testlogger'
        assert event_dict['request_id'] == '9a6172f2e6d2444582f83a6c333d9cfb'
        assert event_dict['server'] == 'ergo-virtual-machine'
        assert event_dict['date'] == datetime.utcnow().date().strftime(
            '%Y-%m-%dT%H:%M:%SZ')
        tags = [('site', 'example.com'),
                ('sys.argv', ["'manage.py'", "'runserver'"]),
                ('price', 6),
                ('tag', "'extra'"),
                ('dupa', True),
                ('project', 'sentry'),
                ('sentry_culprit', 'testlogger in index'),
                ('sentry_language', 'python'),
                ('sentry_release', 'test')]
        assert sorted(event_dict['tags']) == sorted(tags)

    def test_report_payload(self):
        import appenlight.tests.payload_examples as payload_examples
        from appenlight.lib.enums import ParsedSentryEventType
        from appenlight.lib.utils.sentry import parse_sentry_event
        utcnow = datetime.utcnow().date().strftime('%Y-%m-%dT%H:%M:%SZ')
        event_dict, event_type = parse_sentry_event(
            payload_examples.SENTRY_PYTHON_PAYLOAD_7)
        assert ParsedSentryEventType.ERROR_REPORT == event_type
        assert event_dict['client'] == 'sentry'
        assert event_dict[
                   'error'] == 'Exception: test 500 ' \
                               '\u0142\xf3\u201c\u0107\u201c\u0107\u017c\u0105'
        assert event_dict['language'] == 'python'
        assert event_dict['ip'] == '127.0.0.1'
        assert event_dict['request_id'] == '9fae652c8c1c4d6a8eee09260f613a98'
        assert event_dict['server'] == 'ergo-virtual-machine'
        assert event_dict['start_time'] == utcnow
        assert event_dict['url'] == 'http://127.0.0.1:8000/error'
        assert event_dict['user_agent'] == 'Mozilla/5.0 (X11; Linux x86_64) ' \
                                           'AppleWebKit/537.36 (KHTML, ' \
                                           'like Gecko) Chrome/47.0.2526.106 ' \
                                           'Safari/537.36'
        assert event_dict['view_name'] == 'djangoapp.views in error'
        tags = [('site', 'example.com'), ('sentry_release', 'test')]
        assert sorted(event_dict['tags']) == sorted(tags)
        extra = [('sys.argv', ["'manage.py'", "'runserver'"]),
                 ('project', 'sentry')]
        assert sorted(event_dict['extra']) == sorted(extra)
        request = event_dict['request']
        assert request['url'] == 'http://127.0.0.1:8000/error'
        assert request['cookies'] == {'appenlight': 'X'}
        assert request['data'] is None
        assert request['method'] == 'GET'
        assert request['query_string'] == ''
        assert request['env'] == {'REMOTE_ADDR': '127.0.0.1',
                                  'SERVER_NAME': 'localhost',
                                  'SERVER_PORT': '8000'}
        assert request['headers'] == {
            'Accept': 'text/html,application/xhtml+xml,'
                       'application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'en-US,en;q=0.8,pl;q=0.6',
            'Connection': 'keep-alive',
            'Content-Length': '',
            'Content-Type': 'text/plain',
            'Cookie': 'appenlight=X',
            'Dnt': '1',
            'Host': '127.0.0.1:8000',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '
                           'AppleWebKit/537.36 (KHTML, like Gecko) '
                           'Chrome/47.0.2526.106 Safari/537.36'}
        traceback = event_dict['traceback']
        assert traceback[0]['cline'] == 'response = wrapped_callback(request, ' \
                                        '*callback_args, **callback_kwargs)'
        assert traceback[0]['file'] == 'django/core/handlers/base.py'
        assert traceback[0]['fn'] == 'get_response'
        assert traceback[0]['line'] == 111
        assert traceback[0]['module'] == 'django.core.handlers.base'

        assert traceback[1]['cline'] == "raise Exception(u'test 500 " \
                                        "\u0142\xf3\u201c\u0107\u201c\u0107" \
                                        "\u017c\u0105')"
        assert traceback[1]['file'] == 'djangoapp/views.py'
        assert traceback[1]['fn'] == 'error'
        assert traceback[1]['line'] == 84
        assert traceback[1]['module'] == 'djangoapp.views'
        assert sorted(traceback[1]['vars']) == sorted([
            ('c',
             '<sqlite3.Cursor object at 0x7fe7c82af8f0>'),
            ('request',
             '<WSGIRequest at 0x140633490316304>'),
            ('conn',
             '<sqlite3.Connection object at 0x7fe7c8b23bf8>')])


class TestAPIReports_0_5_Validation(object):
    @pytest.mark.parametrize('dummy_json', ['', {}, [], None])
    def test_no_payload(self, dummy_json):
        import colander
        from appenlight.validators import ReportListSchema_0_5
        utcnow = datetime.utcnow()
        schema = ReportListSchema_0_5().bind(utcnow=utcnow)
        with pytest.raises(colander.Invalid):
            schema.deserialize(dummy_json)

    def test_minimal_payload(self):
        dummy_json = [{}]
        import colander
        from appenlight.validators import ReportListSchema_0_5
        utcnow = datetime.utcnow()
        schema = ReportListSchema_0_5().bind(utcnow=utcnow)
        with pytest.raises(colander.Invalid):
            schema.deserialize(dummy_json)

    def test_minimal_payload(self):
        dummy_json = [{'report_details': [{}]}]
        from appenlight.validators import ReportListSchema_0_5
        utcnow = datetime.utcnow()
        schema = ReportListSchema_0_5().bind(utcnow=utcnow)

        deserialized = schema.deserialize(dummy_json)

        expected_deserialization = [
            {'language': 'unknown',
             'server': 'unknown',
             'occurences': 1,
             'priority': 5,
             'view_name': '',
             'client': 'unknown',
             'http_status': 200,
             'error': '',
             'tags': None,
             'username': '',
             'traceback': None,
             'extra': None,
             'url': '',
             'ip': None,
             'start_time': utcnow,
             'group_string': None,
             'request': {},
             'request_stats': None,
             'end_time': None,
             'request_id': '',
             'message': '',
             'slow_calls': [],
             'user_agent': ''
             }
        ]
        assert deserialized == expected_deserialization

    def test_full_payload(self):
        import appenlight.tests.payload_examples as payload_examples
        from appenlight.validators import ReportListSchema_0_5
        PYTHON_PAYLOAD = copy.deepcopy(payload_examples.PYTHON_PAYLOAD_0_5)
        utcnow = datetime.utcnow()
        schema = ReportListSchema_0_5().bind(utcnow=utcnow)
        PYTHON_PAYLOAD["tags"] = [("foo", 1), ("action", "test"), ("baz", 1.1),
                                  ("date",
                                   utcnow.strftime('%Y-%m-%dT%H:%M:%S.0'))]
        dummy_json = [PYTHON_PAYLOAD]
        deserialized = schema.deserialize(dummy_json)[0]
        assert deserialized['error'] == PYTHON_PAYLOAD['error']
        assert deserialized['language'] == PYTHON_PAYLOAD['language']
        assert deserialized['server'] == PYTHON_PAYLOAD['server']
        assert deserialized['priority'] == PYTHON_PAYLOAD['priority']
        assert deserialized['view_name'] == PYTHON_PAYLOAD['view_name']
        assert deserialized['client'] == PYTHON_PAYLOAD['client']
        assert deserialized['http_status'] == PYTHON_PAYLOAD['http_status']
        assert deserialized['error'] == PYTHON_PAYLOAD['error']
        assert deserialized['occurences'] == PYTHON_PAYLOAD['occurences']
        assert deserialized['username'] == PYTHON_PAYLOAD['username']
        assert deserialized['traceback'] == PYTHON_PAYLOAD['traceback']
        assert deserialized['url'] == PYTHON_PAYLOAD['url']
        assert deserialized['ip'] == PYTHON_PAYLOAD['ip']
        assert deserialized['start_time'].strftime('%Y-%m-%dT%H:%M:%S.0') == \
               PYTHON_PAYLOAD['start_time']
        assert deserialized['ip'] == PYTHON_PAYLOAD['ip']
        assert deserialized['group_string'] is None
        assert deserialized['request_stats'] == PYTHON_PAYLOAD['request_stats']
        assert deserialized['end_time'].strftime('%Y-%m-%dT%H:%M:%S.0') == \
               PYTHON_PAYLOAD['end_time']
        assert deserialized['request_id'] == PYTHON_PAYLOAD['request_id']
        assert deserialized['message'] == PYTHON_PAYLOAD['message']
        assert deserialized['user_agent'] == PYTHON_PAYLOAD['user_agent']
        assert deserialized['slow_calls'][0]['start'].strftime(
            '%Y-%m-%dT%H:%M:%S.0') == PYTHON_PAYLOAD['slow_calls'][0][
                   'start']
        assert deserialized['slow_calls'][0]['end'].strftime(
            '%Y-%m-%dT%H:%M:%S.0') == PYTHON_PAYLOAD['slow_calls'][0][
                   'end']
        assert deserialized['slow_calls'][0]['statement'] == \
               PYTHON_PAYLOAD['slow_calls'][0]['statement']
        assert deserialized['slow_calls'][0]['parameters'] == \
               PYTHON_PAYLOAD['slow_calls'][0]['parameters']
        assert deserialized['slow_calls'][0]['type'] == \
               PYTHON_PAYLOAD['slow_calls'][0]['type']
        assert deserialized['slow_calls'][0]['subtype'] == \
               PYTHON_PAYLOAD['slow_calls'][0]['subtype']
        assert deserialized['slow_calls'][0]['location'] == ''
        assert deserialized['tags'] == [
            ('foo', 1), ('action', 'test'),
            ('baz', 1.1), ('date', utcnow.strftime('%Y-%m-%dT%H:%M:%S.0'))]


@pytest.mark.usefixtures('log_schema')
class TestAPILogsValidation(object):
    @pytest.mark.parametrize('dummy_json', ['', {}, [], None])
    def test_no_payload(self, dummy_json, log_schema):
        import colander

        with pytest.raises(colander.Invalid):
            log_schema.deserialize(dummy_json)

    def test_minimal_payload(self, log_schema):
        dummy_json = [{}]
        deserialized = log_schema.deserialize(dummy_json)[0]
        expected = {'log_level': 'UNKNOWN',
                    'namespace': '',
                    'server': 'unknown',
                    'request_id': '',
                    'primary_key': None,
                    'date': datetime.utcnow(),
                    'message': '',
                    'tags': None}
        assert deserialized['log_level'] == expected['log_level']
        assert deserialized['message'] == expected['message']
        assert deserialized['namespace'] == expected['namespace']
        assert deserialized['request_id'] == expected['request_id']
        assert deserialized['server'] == expected['server']
        assert deserialized['tags'] == expected['tags']
        assert deserialized['primary_key'] == expected['primary_key']

    def test_normal_payload(self, log_schema):
        import appenlight.tests.payload_examples as payload_examples
        deserialized = log_schema.deserialize(payload_examples.LOG_EXAMPLES)[0]
        expected = payload_examples.LOG_EXAMPLES[0]
        assert deserialized['log_level'] == expected['log_level']
        assert deserialized['message'] == expected['message']
        assert deserialized['namespace'] == expected['namespace']
        assert deserialized['request_id'] == expected['request_id']
        assert deserialized['server'] == expected['server']
        assert deserialized['date'].strftime('%Y-%m-%dT%H:%M:%S.%f') == \
               expected['date']
        assert deserialized['tags'][0][0] == "tag_name"
        assert deserialized['tags'][0][1] == "tag_value"
        assert deserialized['tags'][1][0] == "tag_name2"
        assert deserialized['tags'][1][1] == 2

    def test_normal_payload_date_without_microseconds(self, log_schema):
        import appenlight.tests.payload_examples as payload_examples
        LOG_EXAMPLE = copy.deepcopy(payload_examples.LOG_EXAMPLES)
        LOG_EXAMPLE[0]['date'] = datetime.utcnow().strftime(
            '%Y-%m-%dT%H:%M:%S')
        deserialized = log_schema.deserialize(LOG_EXAMPLE)
        assert deserialized[0]['date'].strftime('%Y-%m-%dT%H:%M:%S') == \
               LOG_EXAMPLE[0]['date']

    def test_normal_payload_date_without_seconds(self, log_schema):
        import appenlight.tests.payload_examples as payload_examples
        LOG_EXAMPLE = copy.deepcopy(payload_examples.LOG_EXAMPLES)
        LOG_EXAMPLE[0]['date'] = datetime.utcnow().date().strftime(
            '%Y-%m-%dT%H:%M')
        deserialized = log_schema.deserialize(LOG_EXAMPLE)
        assert deserialized[0]['date'].strftime('%Y-%m-%dT%H:%M') == \
               LOG_EXAMPLE[0]['date']

    def test_payload_empty_date(self, log_schema):
        import appenlight.tests.payload_examples as payload_examples
        LOG_EXAMPLE = copy.deepcopy(payload_examples.LOG_EXAMPLES)
        LOG_EXAMPLE[0]['date'] = None
        deserialized = log_schema.deserialize(LOG_EXAMPLE)
        assert deserialized[0]['date'].strftime('%Y-%m-%dT%H:%M') is not None

    def test_payload_no_date(self, log_schema):
        import appenlight.tests.payload_examples as payload_examples
        LOG_EXAMPLE = copy.deepcopy(payload_examples.LOG_EXAMPLES)
        LOG_EXAMPLE[0].pop('date', None)
        deserialized = log_schema.deserialize(LOG_EXAMPLE)
        assert deserialized[0]['date'].strftime('%Y-%m-%dT%H:%M') is not None


@pytest.mark.usefixtures('general_metrics_schema')
class TestAPIGeneralMetricsValidation(object):
    @pytest.mark.parametrize('dummy_json', ['', {}, [], None])
    def test_no_payload(self, dummy_json, general_metrics_schema):
        import colander

        with pytest.raises(colander.Invalid):
            general_metrics_schema.deserialize(dummy_json)

    def test_minimal_payload(self, general_metrics_schema):
        dummy_json = [{'tags': [['counter_a', 15.5], ['counter_b', 63]]}]
        deserialized = general_metrics_schema.deserialize(dummy_json)[0]
        expected = {'namespace': '',
                    'server_name': 'unknown',
                    'tags': [('counter_a', 15.5), ('counter_b', 63)],
                    'timestamp': datetime.utcnow()}
        assert deserialized['namespace'] == expected['namespace']
        assert deserialized['server_name'] == expected['server_name']
        assert deserialized['tags'] == expected['tags']

    def test_normal_payload(self, general_metrics_schema):
        import appenlight.tests.payload_examples as payload_examples
        dummy_json = [payload_examples.METRICS_PAYLOAD]
        deserialized = general_metrics_schema.deserialize(dummy_json)[0]
        expected = {'namespace': 'some.monitor',
                    'server_name': 'server.name',
                    'tags': [('usage_foo', 15.5), ('usage_bar', 63)],
                    'timestamp': datetime.utcnow()}
        assert deserialized['namespace'] == expected['namespace']
        assert deserialized['server_name'] == expected['server_name']
        assert deserialized['tags'] == expected['tags']


@pytest.mark.usefixtures('request_metrics_schema')
class TestAPIRequestMetricsValidation(object):
    @pytest.mark.parametrize('dummy_json', ['', {}, [], None])
    def test_no_payload(self, dummy_json, request_metrics_schema):
        import colander

        with pytest.raises(colander.Invalid):
            print(request_metrics_schema.deserialize(dummy_json))

    def test_normal_payload(self, request_metrics_schema):
        import appenlight.tests.payload_examples as payload_examples
        dummy_json = payload_examples.REQUEST_METRICS_EXAMPLES
        deserialized = request_metrics_schema.deserialize(dummy_json)[0]
        expected = {'metrics': [('dir/module:func',
                                 {'custom': 0.0,
                                  'custom_calls': 0.0,
                                  'main': 0.01664,
                                  'nosql': 0.00061,
                                  'nosql_calls': 23.0,
                                  'remote': 0.0,
                                  'remote_calls': 0.0,
                                  'requests': 1,
                                  'sql': 0.00105,
                                  'sql_calls': 2.0,
                                  'tmpl': 0.0,
                                  'tmpl_calls': 0.0}),
                                ('SomeView.function',
                                 {'custom': 0.0,
                                  'custom_calls': 0.0,
                                  'main': 0.647261,
                                  'nosql': 0.306554,
                                  'nosql_calls': 140.0,
                                  'remote': 0.0,
                                  'remote_calls': 0.0,
                                  'requests': 28,
                                  'sql': 0.0,
                                  'sql_calls': 0.0,
                                  'tmpl': 0.0,
                                  'tmpl_calls': 0.0})],
                    'server': 'some.server.hostname',
                    'timestamp': datetime.utcnow()}
        assert deserialized['server'] == expected['server']
        metric = deserialized['metrics'][0]
        expected_metric = expected['metrics'][0]
        assert metric[0] == expected_metric[0]
        assert sorted(metric[1].items()) == sorted(expected_metric[1].items())


@pytest.mark.usefixtures('default_application')
@pytest.mark.usefixtures('base_app', 'with_migrations', 'clean_tables')
class TestAPIReportsView(object):
    def test_no_json_payload(self, default_application):
        import colander
        from appenlight.models.services.application import ApplicationService
        from appenlight.views.api import reports_create

        context = DummyContext()
        context.resource = ApplicationService.by_id(1)
        request = testing.DummyRequest(
            headers={'Content-Type': 'application/json'})
        request.unsafe_json_body = ''
        request.context = context
        route = mock.Mock()
        route.name = 'api_reports'
        request.matched_route = route
        with pytest.raises(colander.Invalid):
            response = reports_create(request)

    def test_single_proper_json_0_5_payload(self):
        import appenlight.tests.payload_examples as payload_examples
        from appenlight.views.api import reports_create
        from appenlight.models.services.application import ApplicationService
        from appenlight.models.report_group import ReportGroup
        route = mock.Mock()
        route.name = 'api_reports'
        request = pyramid.threadlocal.get_current_request()
        context = DummyContext()
        context.resource = ApplicationService.by_id(1)
        request.context = context
        request.matched_route = route
        PYTHON_PAYLOAD = payload_examples.PYTHON_PAYLOAD_0_5
        request.unsafe_json_body = [copy.deepcopy(PYTHON_PAYLOAD)]
        reports_create(request)
        query = DBSession.query(ReportGroup)
        report = query.first()
        assert query.count() == 1
        assert report.total_reports == 1

    def test_grouping_0_5(self):
        import appenlight.tests.payload_examples as payload_examples
        from appenlight.views.api import reports_create
        from appenlight.models.services.application import ApplicationService
        from appenlight.models.report_group import ReportGroup
        route = mock.Mock()
        route.name = 'api_reports'
        request = pyramid.threadlocal.get_current_request()
        context = DummyContext()
        context.resource = ApplicationService.by_id(1)
        request.context = context
        request.matched_route = route
        PYTHON_PAYLOAD = payload_examples.PYTHON_PAYLOAD_0_5
        request.unsafe_json_body = [copy.deepcopy(PYTHON_PAYLOAD),
                                    copy.deepcopy(PYTHON_PAYLOAD)]
        reports_create(request)
        query = DBSession.query(ReportGroup)
        report = query.first()
        assert query.count() == 1
        assert report.total_reports == 2

    def test_grouping_different_reports_0_5(self):
        import appenlight.tests.payload_examples as payload_examples
        from appenlight.views.api import reports_create
        from appenlight.models.services.application import ApplicationService
        from appenlight.models.report_group import ReportGroup
        route = mock.Mock()
        route.name = 'api_reports'
        request = pyramid.threadlocal.get_current_request()
        context = DummyContext()
        context.resource = ApplicationService.by_id(1)
        request.context = context
        request.matched_route = route
        PYTHON_PAYLOAD = payload_examples.PYTHON_PAYLOAD_0_5
        PARSED_REPORT_404 = payload_examples.PARSED_REPORT_404
        request.unsafe_json_body = [copy.deepcopy(PYTHON_PAYLOAD),
                                    copy.deepcopy(PARSED_REPORT_404)]
        reports_create(request)
        query = DBSession.query(ReportGroup)
        report = query.first()
        assert query.count() == 2
        assert report.total_reports == 1


@pytest.mark.usefixtures('default_application')
@pytest.mark.usefixtures('base_app', 'with_migrations', 'clean_tables')
class TestAirbrakeXMLView(object):

    def test_normal_payload_parsing(self):
        import datetime
        import defusedxml.ElementTree as ElementTree
        import appenlight.tests.payload_examples as payload_examples
        from appenlight.lib.utils.airbrake import parse_airbrake_xml
        from appenlight.validators import ReportListSchema_0_5

        context = DummyContext()
        request = testing.DummyRequest(
            headers={'Content-Type': 'application/xml'})
        request.context = context
        request.context.possibly_public = False
        root = ElementTree.fromstring(payload_examples.AIRBRAKE_RUBY_EXAMPLE)
        request.context.airbrake_xml_etree = root
        error_dict = parse_airbrake_xml(request)
        schema = ReportListSchema_0_5().bind(utcnow=datetime.datetime.utcnow())
        deserialized_report = schema.deserialize([error_dict])[0]
        assert deserialized_report['client'] == 'Airbrake Notifier'
        assert deserialized_report['error'] == 'NameError: undefined local variable or method `sdfdfdf\' for #<#<Class:0x000000039a8b90>:0x00000002c53df0>'
        assert deserialized_report['http_status'] == 500
        assert deserialized_report['language'] == 'unknown'
        assert deserialized_report['message'] == ''
        assert deserialized_report['occurences'] == 1
        assert deserialized_report['priority'] == 5
        d_request = deserialized_report['request']
        assert d_request['GET'] == {'test': '1234'}
        assert d_request['action_dispatch.request.parameters'] == {
            'action': 'index',
            'controller': 'welcome',
            'test': '1234'}
        assert deserialized_report['request_id'] == 'c11b2267f3ad8b00a1768cae35559fa1'
        assert deserialized_report['server'] == 'ergo-desktop'
        assert deserialized_report['traceback'][0] == {
            'cline': 'block in start_thread',
            'file': '/home/ergo/.rbenv/versions/1.9.3-p327/lib/ruby/1.9.1/webrick/server.rb',
            'fn': 'block in start_thread',
            'line': '191',
            'module': '',
            'vars': {}}
        assert deserialized_report['traceback'][-1] == {
            'cline': '_app_views_welcome_index_html_erb___2570061166873166679_31748940',
            'file': '[PROJECT_ROOT]/app/views/welcome/index.html.erb',
            'fn': '_app_views_welcome_index_html_erb___2570061166873166679_31748940',
            'line': '3',
            'module': '',
            'vars': {}}
        assert deserialized_report['url'] == 'http://0.0.0.0:3000/welcome/index?test=1234'
        assert deserialized_report['view_name'] == 'welcome:index'

    def test_normal_payload_view(self):
        import defusedxml.ElementTree as ElementTree
        import appenlight.tests.payload_examples as payload_examples

        from appenlight.models.services.application import ApplicationService
        from appenlight.views.api import airbrake_xml_compat

        context = DummyContext()
        context.resource = ApplicationService.by_id(1)
        request = testing.DummyRequest(
            headers={'Content-Type': 'application/xml'})
        request.context = context
        request.context.possibly_public = False
        root = ElementTree.fromstring(payload_examples.AIRBRAKE_RUBY_EXAMPLE)
        request.context.airbrake_xml_etree = root
        route = mock.Mock()
        route.name = 'api_airbrake'
        request.matched_route = route
        result = airbrake_xml_compat(request)
        assert '<notice><id>' in result


@pytest.mark.usefixtures('default_application')
@pytest.mark.usefixtures('base_app', 'with_migrations', 'clean_tables')
class TestAPILogView(object):
    def test_no_json_payload(self, base_app):
        import colander
        from appenlight.models.services.application import ApplicationService
        from appenlight.views.api import logs_create

        context = DummyContext()
        context.resource = ApplicationService.by_id(1)
        request = testing.DummyRequest(
            headers={'Content-Type': 'application/json'})
        request.context = context
        request.registry = base_app.registry
        request.unsafe_json_body = ''
        route = mock.Mock()
        route.name = 'api_logs'
        request.matched_route = route
        with pytest.raises(colander.Invalid):
            response = logs_create(request)

    def test_single_json_payload(self):
        import appenlight.tests.payload_examples as payload_examples
        from appenlight.models.log import Log
        from appenlight.views.api import logs_create
        from appenlight.models.services.application import ApplicationService
        route = mock.Mock()
        route.name = 'api_logs'
        request = pyramid.threadlocal.get_current_request()
        context = DummyContext()
        context.resource = ApplicationService.by_id(1)
        request.context = context
        request.matched_route = route
        request.unsafe_json_body = [copy.deepcopy(
            payload_examples.LOG_EXAMPLES[0])]
        logs_create(request)
        query = DBSession.query(Log)
        log = query.first()
        assert query.count() == 1
        assert log.message == "OMG ValueError happened"

    def test_multiple_json_payload(self):
        import appenlight.tests.payload_examples as payload_examples
        from appenlight.models.log import Log
        from appenlight.views.api import logs_create
        from appenlight.models.services.application import ApplicationService
        route = mock.Mock()
        route.name = 'api_logs'
        request = pyramid.threadlocal.get_current_request()
        context = DummyContext()
        context.resource = ApplicationService.by_id(1)
        request.context = context
        request.matched_route = route
        LOG_PAYLOAD = payload_examples.LOG_EXAMPLES[0]
        LOG_PAYLOAD2 = payload_examples.LOG_EXAMPLES[1]
        request.unsafe_json_body = copy.deepcopy([LOG_PAYLOAD, LOG_PAYLOAD2])
        logs_create(request)
        query = DBSession.query(Log).order_by(sa.asc(Log.log_id))
        assert query.count() == 2
        assert query[0].message == "OMG ValueError happened"
        assert query[1].message == "OMG ValueError happened2"

    def test_public_key_rewriting(self):
        import appenlight.tests.payload_examples as payload_examples
        from appenlight.models.log import Log
        from appenlight.views.api import logs_create
        from appenlight.models.services.application import ApplicationService
        route = mock.Mock()
        route.name = 'api_logs'
        request = pyramid.threadlocal.get_current_request()
        context = DummyContext()
        context.resource = ApplicationService.by_id(1)
        request.context = context
        request.matched_route = route

        LOG_PAYLOAD = copy.deepcopy(payload_examples.LOG_EXAMPLES[0])
        LOG_PAYLOAD2 = copy.deepcopy(payload_examples.LOG_EXAMPLES[1])
        LOG_PAYLOAD['primary_key'] = 'X2'
        LOG_PAYLOAD2['primary_key'] = 'X2'
        request.unsafe_json_body = [LOG_PAYLOAD, LOG_PAYLOAD2]
        logs_create(request)

        query = DBSession.query(Log).order_by(sa.asc(Log.log_id))
        assert query.count() == 1
        assert query[0].message == "OMG ValueError happened2"

@pytest.mark.usefixtures('default_application')
@pytest.mark.usefixtures('base_app', 'with_migrations', 'clean_tables')
class TestAPIGeneralMetricsView(object):
    def test_no_json_payload(self, base_app):
        import colander
        from appenlight.models.services.application import ApplicationService
        from appenlight.views.api import general_metrics_create
        route = mock.Mock()
        route.name = 'api_general_metrics'
        context = DummyContext()
        context.resource = ApplicationService.by_id(1)
        request = testing.DummyRequest(
            headers={'Content-Type': 'application/json'})
        request.context = context
        request.registry = base_app.registry
        request.unsafe_json_body = ''
        request.matched_route = route
        with pytest.raises(colander.Invalid):
            general_metrics_create(request)

    def test_single_json_payload(self):
        import appenlight.tests.payload_examples as payload_examples
        from appenlight.models.metric import Metric
        from appenlight.views.api import general_metrics_create
        from appenlight.models.services.application import ApplicationService
        route = mock.Mock()
        route.name = 'api_general_metric'
        request = pyramid.threadlocal.get_current_request()
        request.matched_route = route
        context = DummyContext()
        context.resource = ApplicationService.by_id(1)
        request.context = context
        request.unsafe_json_body = payload_examples.METRICS_PAYLOAD
        general_metrics_create(request)
        query = DBSession.query(Metric)
        metric = query.first()
        assert query.count() == 1
        assert metric.namespace == 'some.monitor'

    def test_multiple_json_payload(self):
        import appenlight.tests.payload_examples as payload_examples
        from appenlight.models.metric import Metric
        from appenlight.views.api import general_metrics_create
        from appenlight.models.services.application import ApplicationService
        route = mock.Mock()
        route.name = 'api_general_metrics'
        request = pyramid.threadlocal.get_current_request()
        request.matched_route = route
        context = DummyContext()
        context.resource = ApplicationService.by_id(1)
        request.context = context
        request.unsafe_json_body = [
            copy.deepcopy(payload_examples.METRICS_PAYLOAD),
            copy.deepcopy(payload_examples.METRICS_PAYLOAD),
        ]
        general_metrics_create(request)
        query = DBSession.query(Metric)
        metric = query.first()
        assert query.count() == 2
        assert metric.namespace == 'some.monitor'


class TestGroupingMessageReplacements(object):
    def replace_default_repr_python(self):
        test_str = '''
        ConnectionError: ConnectionError((<urllib3.connection.HTTPConnection object at 0x7f87a0ba9fd0>, 'Connection to domain.gr timed out. (connect timeout=10)')) caused by: ConnectTimeoutError((<urllib3.connection.HTTPConnection object at 0x7f87a0ba9fd0>, 'Connection to domain.gr timed out. (connect timeout=10)'))
        '''
        regex = r'<(.*?) object at (.*?)>'


class TestRulesKeyGetter(object):
    def test_default_dict_getter_top_key(self):
        from appenlight.lib.rule import Rule
        struct = {
            "a": {
                "b": 'b',
                "c": {
                    "d": 'd',
                    "g": {
                        "h": 'h'
                    }
                },
                "e": 'e'
            },
            "f": 'f'
        }
        result = Rule.default_dict_struct_getter(struct, "a")
        assert result == struct['a']

    def test_default_dict_getter_sub_key(self):
        from appenlight.lib.rule import Rule
        struct = {
            "a": {
                "b": 'b',
                "c": {
                    "d": 'd',
                    "g": {
                        "h": 'h'
                    }
                },
                "e": 'e'
            },
            "f": 'f'
        }
        result = Rule.default_dict_struct_getter(struct, 'a:b')
        assert result == struct['a']['b']
        result = Rule.default_dict_struct_getter(struct, 'a:c:d')
        assert result == struct['a']['c']['d']

    def test_default_obj_getter_top_key(self):
        from appenlight.lib.rule import Rule
        class TestStruct(object):
            def __init__(self, a, b):
                self.a = a
                self.b = b

        struct = TestStruct(a='a',
                            b=TestStruct(a='x', b='y'))
        result = Rule.default_obj_struct_getter(struct, "a")
        assert result == struct.a

    def test_default_obj_getter_sub_key(self):
        from appenlight.lib.rule import Rule
        class TestStruct(object):
            def __init__(self, name, a, b):
                self.name = name
                self.a = a
                self.b = b

            def __repr__(self):
                return '<obj {}>'.format(self.name)

        c = TestStruct('c', a=5, b='z')
        b = TestStruct('b', a=c, b='y')
        struct = TestStruct('a', a='a', b=b)
        result = Rule.default_obj_struct_getter(struct, 'b:b')
        assert result == struct.b.b
        result = Rule.default_obj_struct_getter(struct, 'b:a:b')
        assert result == struct.b.a.b


@pytest.mark.usefixtures('report_type_matrix')
class TestRulesParsing():
    @pytest.mark.parametrize("op, struct_value, test_value, match_result", [
        ('eq', 500, 500, True),
        ('eq', 600, 500, False),
        ('eq', 300, 500, False),
        ('eq', "300", 500, False),
        ('eq', "600", 500, False),
        ('eq', "500", 500, True),
        ('ne', 500, 500, False),
        ('ne', 600, 500, True),
        ('ne', 300, 500, True),
        ('ne', "300", 500, True),
        ('ne', "600", 500, True),
        ('ne', "500", 500, False),
        ('ge', 500, 500, True),
        ('ge', 600, 500, True),
        ('ge', 499, 500, False),
        ('gt', 499, 500, False),
        ('gt', 500, 500, False),
        ('gt', 501, 500, True),
        ('le', 499, 500, True),
        ('le', 500, 500, True),
        ('le', 501, 500, False),
        ('lt', 499, 500, True),
        ('lt', 500, 500, False),
        ('lt', 501, 500, False),
    ])
    def test_single_op_int(self, op, struct_value, test_value, match_result,
                           report_type_matrix):
        from appenlight.lib.rule import Rule
        rule_config = {
            "op": op,
            "field": "http_status",
            "value": test_value
        }
        rule = Rule(rule_config, report_type_matrix)

        data = {
            "http_status": struct_value
        }
        assert rule.match(data) is match_result

    @pytest.mark.parametrize("op, struct_value, test_value, match_result", [
        ('ge', "500.01", 500, True),
        ('ge', "500.01", 500.02, False),
        ('le', "500.01", 500.02, True)
    ])
    def test_single_op_float(self, op, struct_value, test_value, match_result,
                             report_type_matrix):
        from appenlight.lib.rule import Rule
        rule_config = {
            "op": op,
            "field": "duration",
            "value": test_value
        }
        rule = Rule(rule_config, report_type_matrix)

        data = {
            "duration": struct_value
        }
        assert rule.match(data) is match_result

    @pytest.mark.parametrize("op, struct_value, test_value, match_result", [
        ('contains', 'foo bar baz', 'foo', True),
        ('contains', 'foo bar baz', 'bar', True),
        ('contains', 'foo bar baz', 'dupa', False),
        ('startswith', 'foo bar baz', 'foo', True),
        ('startswith', 'foo bar baz', 'bar', False),
        ('endswith', 'foo bar baz', 'baz', True),
        ('endswith', 'foo bar baz', 'bar', False),
    ])
    def test_single_op_string(self, op, struct_value, test_value,
                              match_result, report_type_matrix):
        from appenlight.lib.rule import Rule
        rule_config = {
            "op": op,
            "field": "error",
            "value": test_value
        }
        rule = Rule(rule_config, report_type_matrix)

        data = {
            "error": struct_value
        }
        assert rule.match(data) is match_result

    @pytest.mark.parametrize("field, value, s_type", [
        ('field_unicode', 500, str),
        ('field_unicode', 500.0, str),
        ('field_unicode', "500", str),
        ('field_int', "500", int),
        ('field_int', 500, int),
        ('field_int', 500.0, int),
        ('field_float', "500", float),
        ('field_float', 500, float),
        ('field_float', 500.0, float),
    ])
    def test_type_normalization(self, field, value, s_type):
        from appenlight.lib.rule import Rule
        type_matrix = {
            'field_unicode': {"type": 'unicode'},
            'field_float': {"type": 'float'},
            'field_int': {"type": 'int'},
        }

        rule = Rule({}, type_matrix)
        n_value = rule.normalized_type(field, value)
        assert isinstance(n_value, s_type) is True


@pytest.mark.usefixtures('report_type_matrix')
class TestNestedRuleParsing():

    @pytest.mark.parametrize("data, result", [
        ({"http_status": 501, "group": {"priority": 7, "occurences": 11}},
         False),
        ({"http_status": 101, "group": {"priority": 7, "occurences": 11}},
         False),
        ({"http_status": 500, "group": {"priority": 1, "occurences": 11}},
         False),
        ({"http_status": 101, "group": {"priority": 3, "occurences": 5}},
         True),
    ])
    def test_NOT_rule(self, data, result, report_type_matrix):
        from appenlight.lib.rule import Rule
        rule_config = {
            "field": "__NOT__",
            "rules": [
                {
                    "op": "ge",
                    "field": "group:occurences",
                    "value": "10"
                },
                {
                    "op": "ge",
                    "field": "group:priority",
                    "value": "4"
                }
            ]
        }

        rule = Rule(rule_config, report_type_matrix)
        assert rule.match(data) is result

    @pytest.mark.parametrize("data, result", [
        ({"http_status": 501, "group": {"priority": 7, "occurences": 11}},
         True),
        ({"http_status": 101, "group": {"priority": 7, "occurences": 11}},
         True),
        ({"http_status": 500, "group": {"priority": 1, "occurences": 1}},
         True),
        ({"http_status": 101, "group": {"priority": 3, "occurences": 11}},
         False),
    ])
    def test_nested_OR_AND_rule(self, data, result, report_type_matrix):
        from appenlight.lib.rule import Rule
        rule_config = {
            "field": "__OR__",
            "rules": [
                {
                    "field": "__AND__",
                    "rules": [
                        {
                            "op": "ge",
                            "field": "group:occurences",
                            "value": "10"
                        },
                        {
                            "op": "ge",
                            "field": "group:priority",
                            "value": "4"
                        }
                    ]
                },
                {
                    "op": "eq",
                    "field": "http_status",
                    "value": "500"
                }
            ]
        }

        rule = Rule(rule_config, report_type_matrix)
        assert rule.match(data) is result

    @pytest.mark.parametrize("data, result", [
        ({"http_status": 501, "group": {"priority": 7, "occurences": 11}},
         True),
        ({"http_status": 101, "group": {"priority": 7, "occurences": 11}},
         True),
        ({"http_status": 500, "group": {"priority": 1, "occurences": 1}},
         True),
        ({"http_status": 101, "group": {"priority": 3, "occurences": 1}},
         False),
    ])
    def test_nested_OR_OR_rule(self, data, result, report_type_matrix):
        from appenlight.lib.rule import Rule
        rule_config = {
            "field": "__OR__",
            "rules": [
                {"field": "__OR__",
                 "rules": [
                     {"op": "ge",
                      "field": "group:occurences",
                      "value": "10"
                      },
                     {"op": "ge",
                      "field": "group:priority",
                      "value": "4"
                      }
                 ]
                 },
                {"op": "eq",
                 "field": "http_status",
                 "value": "500"
                 }
            ]
        }

        rule = Rule(rule_config, report_type_matrix)
        assert rule.match(data) is result

    @pytest.mark.parametrize("data, result", [
        ({"http_status": 500, "group": {"priority": 7, "occurences": 11}},
         True),
        ({"http_status": 101, "group": {"priority": 7, "occurences": 11}},
         False),
        ({"http_status": 500, "group": {"priority": 1, "occurences": 1}},
         False),
        ({"http_status": 101, "group": {"priority": 3, "occurences": 1}},
         False),
    ])
    def test_nested_AND_AND_rule(self, data, result, report_type_matrix):
        from appenlight.lib.rule import Rule
        rule_config = {
            "field": "__AND__",
            "rules": [
                {"field": "__AND__",
                 "rules": [
                     {"op": "ge",
                      "field": "group:occurences",
                      "value": "10"
                      },
                     {"op": "ge",
                      "field": "group:priority",
                      "value": "4"
                      }]
                 },
                {"op": "eq",
                 "field": "http_status",
                 "value": "500"
                 }
            ]
        }

        rule = Rule(rule_config, report_type_matrix)
        assert rule.match(data) is result

    @pytest.mark.parametrize("data, result", [
        ({"http_status": 500, "group": {"priority": 7, "occurences": 11},
          "url_path": '/test/register', "error": "foo test bar"}, True),
        ({"http_status": 500, "group": {"priority": 7, "occurences": 11},
          "url_path": '/test/register', "error": "foo INVALID bar"}, False),
    ])
    def test_nested_AND_AND_AND_rule(self, data, result, report_type_matrix):
        from appenlight.lib.rule import Rule
        rule_config = {
            "field": "__AND__",
            "rules": [
                {"field": "__AND__",
                 "rules": [
                     {"op": "ge",
                      "field": "group:occurences",
                      "value": "10"
                      },
                     {"field": "__AND__",
                      "rules": [
                          {"op": "endswith",
                           "field": "url_path",
                           "value": "register"},
                          {"op": "contains",
                           "field": "error",
                           "value": "test"}]}]
                 },
                {"op": "eq",
                 "field": "http_status",
                 "value": "500"
                 }
            ]
        }

        rule = Rule(rule_config, report_type_matrix)
        assert rule.match(data) is result

    @pytest.mark.parametrize("data, result", [
        ({"http_status": 500, "group": {"priority": 7, "occurences": 11},
          "url_path": 6, "error": 3}, False),
        ({"http_status": 500, "group": {"priority": 7, "occurences": 11},
          "url_path": '/test/register', "error": "foo INVALID bar"}, True),
    ])
    def test_nested_AND_AND_OR_rule(self, data, result, report_type_matrix):
        from appenlight.lib.rule import Rule
        rule_config = {
            "field": "__AND__",
            "rules": [
                {"field": "__AND__",
                 "rules": [
                     {"op": "ge",
                      "field": "group:occurences",
                      "value": "10"
                      },
                     {"field": "__OR__",
                      "rules": [
                          {"op": "endswith",
                           "field": "url_path",
                           "value": "register"
                           },
                          {"op": "contains",
                           "field": "error",
                           "value": "test"
                           }]}]
                 },
                {"op": "eq",
                 "field": "http_status",
                 "value": "500"
                 }
            ]
        }

        rule = Rule(rule_config, report_type_matrix)
        assert rule.match(data) is result

    @pytest.mark.parametrize("op, field, value, should_fail", [
        ('eq', 'http_status', "1", False),
        ('ne', 'http_status', "1", False),
        ('ne', 'http_status', "foo", True),
        ('startswith', 'http_status', "1", True),
        ('eq', 'group:priority', "1", False),
        ('ne', 'group:priority', "1", False),
        ('ge', 'group:priority', "1", False),
        ('le', 'group:priority', "1", False),
        ('startswith', 'group:priority', "1", True),
        ('eq', 'url_domain', "1", False),
        ('ne', 'url_domain', "1", False),
        ('startswith', 'url_domain', "1", False),
        ('endswith', 'url_domain', "1", False),
        ('contains', 'url_domain', "1", False),
        ('ge', 'url_domain', "1", True),
        ('eq', 'url_path', "1", False),
        ('ne', 'url_path', "1", False),
        ('startswith', 'url_path', "1", False),
        ('endswith', 'url_path', "1", False),
        ('contains', 'url_path', "1", False),
        ('ge', 'url_path', "1", True),
        ('eq', 'error', "1", False),
        ('ne', 'error', "1", False),
        ('startswith', 'error', "1", False),
        ('endswith', 'error', "1", False),
        ('contains', 'error', "1", False),
        ('ge', 'error', "1", True),
        ('ge', 'url_path', "1", True),
        ('eq', 'tags:server_name', "1", False),
        ('ne', 'tags:server_name', "1", False),
        ('startswith', 'tags:server_name', "1", False),
        ('endswith', 'tags:server_name', "1", False),
        ('contains', 'tags:server_name', "1", False),
        ('ge', 'tags:server_name', "1", True),
        ('contains', 'traceback', "1", False),
        ('ge', 'traceback', "1", True),
        ('eq', 'group:occurences', "1", False),
        ('ne', 'group:occurences', "1", False),
        ('ge', 'group:occurences', "1", False),
        ('le', 'group:occurences', "1", False),
        ('contains', 'group:occurences', "1", True),
    ])
    def test_rule_validation(self, op, field, value, should_fail,
                             report_type_matrix):
        import colander
        from appenlight.validators import build_rule_schema
        rule_config = {
            "op": op,
            "field": field,
            "value": value
        }

        schema = build_rule_schema(rule_config, report_type_matrix)
        if should_fail:
            with pytest.raises(colander.Invalid):
                schema.deserialize(rule_config)
        else:
            schema.deserialize(rule_config)

    def test_nested_proper_rule_validation(self, report_type_matrix):
        from appenlight.validators import build_rule_schema
        rule_config = {
            "field": "__AND__",
            "rules": [
                {
                    "field": "__AND__",
                    "rules": [
                        {
                            "op": "ge",
                            "field": "group:occurences",
                            "value": "10"
                        },
                        {
                            "field": "__OR__",
                            "rules": [
                                {
                                    "op": "endswith",
                                    "field": "url_path",
                                    "value": "register"
                                },
                                {
                                    "op": "contains",
                                    "field": "error",
                                    "value": "test"
                                }
                            ]
                        }
                    ]
                },
                {
                    "op": "eq",
                    "field": "http_status",
                    "value": "500"
                }
            ]
        }

        schema = build_rule_schema(rule_config, report_type_matrix)
        deserialized = schema.deserialize(rule_config)

    def test_nested_bad_rule_validation(self, report_type_matrix):
        import colander
        from appenlight.validators import build_rule_schema
        rule_config = {
            "field": "__AND__",
            "rules": [
                {
                    "field": "__AND__",
                    "rules": [
                        {
                            "op": "ge",
                            "field": "group:occurences",
                            "value": "10"
                        },
                        {
                            "field": "__OR__",
                            "rules": [
                                {
                                    "op": "gt",
                                    "field": "url_path",
                                    "value": "register"
                                },
                                {
                                    "op": "contains",
                                    "field": "error",
                                    "value": "test"
                                }
                            ]
                        }
                    ]
                },
                {
                    "op": "eq",
                    "field": "http_status",
                    "value": "500"
                }
            ]
        }

        schema = build_rule_schema(rule_config, report_type_matrix)
        with pytest.raises(colander.Invalid):
            deserialized = schema.deserialize(rule_config)

    def test_config_manipulator(self):
        from appenlight.lib.rule import Rule
        type_matrix = {
            'a': {"type": 'int',
                  "ops": ('eq', 'ne', 'ge', 'le',)},
            'b': {"type": 'int',
                  "ops": ('eq', 'ne', 'ge', 'le',)},
        }
        rule_config = {
            "field": "__OR__",
            "rules": [
                {
                    "field": "__OR__",
                    "rules": [
                        {
                            "op": "ge",
                            "field": "a",
                            "value": "10"
                        }
                    ]
                },
                {
                    "op": "eq",
                    "field": "b",
                    "value": "500"
                }
            ]
        }

        def rule_manipulator(rule):
            if 'value' in rule.config:
                rule.config['value'] = "1"

        rule = Rule(rule_config, type_matrix,
                    config_manipulator=rule_manipulator)
        rule.match({"a": 1,
                    "b": "2"})
        assert rule.config['rules'][0]['rules'][0]['value'] == "1"
        assert rule.config['rules'][1]['value'] == "1"
        assert rule.type_matrix["b"]['type'] == "int"

    def test_dynamic_config_manipulator(self):
        from appenlight.lib.rule import Rule
        rule_config = {
            "field": "__OR__",
            "rules": [
                {
                    "field": "__OR__",
                    "rules": [
                        {
                            "op": "ge",
                            "field": "a",
                            "value": "10"
                        }
                    ]
                },
                {
                    "op": "eq",
                    "field": "b",
                    "value": "500"
                }
            ]
        }

        def rule_manipulator(rule):
            rule.type_matrix = {
                'a': {"type": 'int',
                      "ops": ('eq', 'ne', 'ge', 'le',)},
                'b': {"type": 'unicode',
                      "ops": ('eq', 'ne', 'ge', 'le',)},
            }

            if 'value' in rule.config:
                if rule.config['field'] == 'a':
                    rule.config['value'] = "1"
                elif rule.config['field'] == 'b':
                    rule.config['value'] = "2"

        rule = Rule(rule_config, {},
                    config_manipulator=rule_manipulator)
        rule.match({"a": 11,
                    "b": "55"})
        assert rule.config['rules'][0]['rules'][0]['value'] == "1"
        assert rule.config['rules'][1]['value'] == "2"
        assert rule.type_matrix["b"]['type'] == "unicode"


@pytest.mark.usefixtures('base_app', 'with_migrations')
class TestViewsWithForms(object):
    def test_bad_csrf(self):
        from appenlight.forms import CSRFException
        from appenlight.views.index import register
        post_data = {'dupa': 'dupa'}
        request = testing.DummyRequest(post=post_data)
        request.POST = webob.multidict.MultiDict(request.POST)
        with pytest.raises(CSRFException):
            register(request)

    def test_proper_csrf(self):
        from appenlight.views.index import register
        request = pyramid.threadlocal.get_current_request()
        post_data = {'dupa': 'dupa',
                     'csrf_token': request.session.get_csrf_token()}
        request = testing.DummyRequest(post=post_data)
        request.POST = webob.multidict.MultiDict(request.POST)
        result = register(request)
        assert result['form'].errors['email'][0] == 'This field is required.'


@pytest.mark.usefixtures('base_app', 'with_migrations', 'default_data')
class TestRegistration(object):
    def test_invalid_form(self):
        from appenlight.views.index import register
        request = pyramid.threadlocal.get_current_request()
        post_data = {'user_name': '',
                     'user_password': '',
                     'email': '',
                     'csrf_token': request.session.get_csrf_token()}
        request = testing.DummyRequest(post=post_data)
        request.POST = webob.multidict.MultiDict(request.POST)
        result = register(request)
        assert result['form'].errors['user_name'][0] == \
               'This field is required.'

    def test_valid_form(self):
        from appenlight.views.index import register
        from ziggurat_foundations.models.services.user import UserService
        request = pyramid.threadlocal.get_current_request()
        post_data = {'user_name': 'foo',
                     'user_password': 'barr',
                     'email': 'test@test.foo',
                     'csrf_token': request.session.get_csrf_token()}
        request = testing.DummyRequest(post=post_data)
        request.add_flash_to_headers = mock.Mock()
        request.POST = webob.multidict.MultiDict(request.POST)
        assert UserService.by_user_name('foo') is None
        register(request)
        user = UserService.by_user_name('foo')
        assert user.user_name == 'foo'
        assert len(user.user_password) == 60


@pytest.mark.usefixtures('base_app', 'with_migrations', 'clean_tables',
                         'default_user')
class TestApplicationCreation(object):
    def test_wrong_data(self):
        import appenlight.views.applications as applications
        from ziggurat_foundations.models.services.user import UserService
        request = pyramid.threadlocal.get_current_request()
        request.user = UserService.by_user_name('testuser')
        request.unsafe_json_body = {}
        request.headers['X-XSRF-TOKEN'] = request.session.get_csrf_token()
        response = applications.application_create(request)
        assert response.code == 422

    def test_proper_data(self):
        import appenlight.views.applications as applications
        from ziggurat_foundations.models.services.user import UserService

        request = pyramid.threadlocal.get_current_request()
        request.user = UserService.by_user_name('testuser')
        request.unsafe_json_body = {"resource_name": "app name",
                                    "domains": "foo"}
        request.headers['X-XSRF-TOKEN'] = request.session.get_csrf_token()
        app_dict = applications.application_create(request)
        assert app_dict['public_key'] is not None
        assert app_dict['api_key'] is not None
        assert app_dict['resource_name'] == 'app name'
        assert app_dict['owner_group_id'] is None
        assert app_dict['resource_id'] is not None
        assert app_dict['default_grouping'] == 'url_traceback'
        assert app_dict['possible_permissions'] == ('view', 'update_reports')
        assert app_dict['slow_report_threshold'] == 10
        assert app_dict['owner_user_name'] == 'testuser'
        assert app_dict['owner_user_id'] == request.user.id
        assert app_dict['domains'] is 'foo'
        assert app_dict['postprocessing_rules'] == []
        assert app_dict['error_report_threshold'] == 10
        assert app_dict['allow_permanent_storage'] is False
        assert app_dict['resource_type'] == 'application'
        assert app_dict['current_permissions'] == []


@pytest.mark.usefixtures('default_application')
@pytest.mark.usefixtures('base_app', 'with_migrations', 'clean_tables')
class TestAPISentryView(object):
    def test_no_payload(self, default_application):
        import colander
        from appenlight.models.services.application import ApplicationService
        from appenlight.views.api import sentry_compat
        from appenlight.lib.request import JSONException

        context = DummyContext()
        context.resource = ApplicationService.by_id(1)
        request = testing.DummyRequest(
            headers={'Content-Type': 'application/json'})
        request.unsafe_json_body = ''
        request.context = context
        route = mock.Mock()
        route.name = 'api_sentry'
        request.matched_route = route
        with pytest.raises(JSONException):
            sentry_compat(request)

    def test_java_client_payload(self):
        from appenlight.views.api import sentry_compat
        from appenlight.models.services.application import ApplicationService
        from appenlight.models.report_group import ReportGroup
        route = mock.Mock()
        route.name = 'api_sentry'
        request = pyramid.threadlocal.get_current_request()
        context = DummyContext()
        context.resource = ApplicationService.by_id(1)
        context.resource.allow_permanent_storage = True
        request.context = context
        request.matched_route = route
        request.body = b'eJy1UmFr2zAQ/S0T+7BCLOzYThp/C6xjG6SDLd/GCBf57Ki' \
                       b'RJSHJJiXkv+/UlC7p2kAZA33Ru6f33t1pz3BAHVayZhWr87' \
                       b'JMs+I6q3MsrifFep2vc1iXM1HMpgBTNmIdeg8tEvlmJ9AGa' \
                       b'fQ7goOkQoDOUmGcZpMkLZO0WGZFRadMiaHIR1EVnTMu3k3b' \
                       b'oiMgqJrXpgOpOVjLLTiPkWAVhMa4jih3MAAholfWyUDAksz' \
                       b'm1iopICbg8fWH52B8VWXZVYwHrWfV/jBipD2gW2no8CFMa5' \
                       b'JButCDSjoQG6mR6LgLDojPPn/7sbydL25ep34HGl+y3DiE+' \
                       b'lH0xXBXjMzFBsXW99SS7pWKYXRw91zqgK4BgZ4/DZVVP/cs' \
                       b'3NuzSZPfAKqP2Cdj4tw7U/cKH0fEFeiWQFqE2FIHAmMPjaN' \
                       b'Y/kHvbzY/JqdHUq9o/KxqQHkcsabX4piDuT4aK+pXG1ZNi/' \
                       b'IwOpEyruXC1LiB3vPO3BmOOxTUCIqv5LIg5H12oh9cf0l+P' \
                       b'MvP5P8kddgoFIEvMGzM5cRSD2aLJ6qTdHKm6nv9pPcRFba0' \
                       b'Kd0eleeCFuGN+9JZ9TaXIn/V5JYMBvxXg3L6PwzSE4dkfOb' \
                       b'w7CtfWmP85SdCs8OvA53fUV19cg=='
        sentry_compat(request)
        query = DBSession.query(ReportGroup)
        report = query.first()
        assert query.count() == 1
        assert report.total_reports == 1

    def test_ruby_client_payload(self):
        from appenlight.views.api import sentry_compat
        from appenlight.models.services.application import ApplicationService
        from appenlight.models.report_group import ReportGroup
        from appenlight.tests.payload_examples import SENTRY_RUBY_ENCODED
        route = mock.Mock()
        route.name = 'api_sentry'
        request = testing.DummyRequest(
            headers={'Content-Type': 'application/octet-stream',
                     'User-Agent': 'sentry-ruby/1.0.0',
                     'X-Sentry-Auth': 'Sentry sentry_version=5, '
                                      'sentry_client=raven-ruby/1.0.0, '
                                      'sentry_timestamp=1462378483, '
                                      'sentry_key=xxx, sentry_secret=xxx'
                     })
        context = DummyContext()
        context.resource = ApplicationService.by_id(1)
        context.resource.allow_permanent_storage = True
        request.context = context
        request.matched_route = route
        request.body = SENTRY_RUBY_ENCODED
        sentry_compat(request)
        query = DBSession.query(ReportGroup)
        report = query.first()
        assert query.count() == 1
        assert report.total_reports == 1

    def test_python_client_decoded_payload(self):
        from appenlight.views.api import sentry_compat
        from appenlight.models.services.application import ApplicationService
        from appenlight.models.report_group import ReportGroup
        from appenlight.tests.payload_examples import SENTRY_PYTHON_PAYLOAD_7
        route = mock.Mock()
        route.name = 'api_sentry'
        request = pyramid.threadlocal.get_current_request()
        context = DummyContext()
        context.resource = ApplicationService.by_id(1)
        context.resource.allow_permanent_storage = True
        request.context = context
        request.matched_route = route
        request.body = json.dumps(SENTRY_PYTHON_PAYLOAD_7).encode('utf8')
        sentry_compat(request)
        query = DBSession.query(ReportGroup)
        report = query.first()
        assert query.count() == 1
        assert report.total_reports == 1

    def test_python_client_encoded_payload(self):
        from appenlight.views.api import sentry_compat
        from appenlight.models.services.application import ApplicationService
        from appenlight.models.report_group import ReportGroup
        from appenlight.tests.payload_examples import SENTRY_PYTHON_ENCODED
        route = mock.Mock()
        route.name = 'api_sentry'
        request = testing.DummyRequest(
            headers={'Content-Type': 'application/octet-stream',
                     'Content-Encoding': 'deflate',
                     'User-Agent': 'sentry-ruby/1.0.0',
                     'X-Sentry-Auth': 'Sentry sentry_version=5, '
                                      'sentry_client=raven-ruby/1.0.0, '
                                      'sentry_timestamp=1462378483, '
                                      'sentry_key=xxx, sentry_secret=xxx'
                     })
        context = DummyContext()
        context.resource = ApplicationService.by_id(1)
        context.resource.allow_permanent_storage = True
        request.context = context
        request.matched_route = route
        request.body = SENTRY_PYTHON_ENCODED
        sentry_compat(request)
        query = DBSession.query(ReportGroup)
        report = query.first()
        assert query.count() == 1
        assert report.total_reports == 1
