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
import pytest
import json
from webtest import TestApp


@pytest.mark.usefixtures('base_app', 'with_migrations', 'clean_tables',
                         'default_application')
class TestIntegrationAPIReportsView(object):
    def test_no_json_payload(self, base_app):
        app = TestApp(base_app)
        url_path = '/api/reports'
        headers = {'x-appenlight-api-key': 'xxxx'}
        res = app.post(url_path, {}, status=400,
                       headers=headers)

    def test_wrong_json_payload(self, base_app):
        app = TestApp(base_app)
        url_path = '/api/reports'
        headers = {'x-appenlight-api-key': 'xxxx'}
        res = app.post(url_path, {}, status=400, headers=headers)

    def test_correct_json_payload(self, base_app):
        import appenlight.tests.payload_examples as payload_examples
        app = TestApp(base_app)
        url_path = '/api/reports'
        headers = {'x-appenlight-api-key': 'xxxx'}
        res = app.post_json(url_path, [payload_examples.PYTHON_PAYLOAD_0_5],
                            headers=headers)

    def test_json_payload_wrong_key(self, base_app):
        import appenlight.tests.payload_examples as payload_examples
        app = TestApp(base_app)
        url_path = '/api/reports'
        res = app.post(url_path,
                       json.dumps([payload_examples.PYTHON_PAYLOAD_0_5]),
                       status=403)


@pytest.mark.usefixtures('base_app', 'with_migrations', 'clean_tables',
                         'default_data', 'default_application')
class TestIntegrationRegistrationView(object):
    def test_register_empty(self, base_app):
        url_path = '/register'
        app = TestApp(base_app)
        resp = app.get('/')
        cookies = resp.headers.getall('Set-Cookie')
        cookie = None
        for name, value in [c.split('=', 1) for c in cookies]:
            if name == 'XSRF-TOKEN':
                cookie = value.split(';')[0]
        headers = {'X-XSRF-TOKEN': cookie}
        res = app.post(url_path,
                       params={'user_name': '',
                               'user_password': '',
                               'email': ''},
                       headers=headers)
        assert 'This field is required.' in res

    def test_register_proper(self, base_app):
        url_path = '/register'
        app = TestApp(base_app)
        resp = app.get('/')
        cookies = resp.headers.getall('Set-Cookie')
        cookie = None
        for name, value in [c.split('=', 1) for c in cookies]:
            if name == 'XSRF-TOKEN':
                cookie = value.split(';')[0]
        headers = {'X-XSRF-TOKEN': cookie}
        res = app.post(url_path,
                       params={'user_name': 'user_foo',
                               'user_password': 'passbar',
                               'email': 'foobar@blablabla.com'},
                       headers=headers,
                       status=302)


@pytest.mark.usefixtures('base_app', 'with_migrations', 'clean_tables',
                         'default_data', 'default_application')
class TestIntegrationRegistrationAuthTokenView(object):

    def test_create_application_bad(self, base_app):
        url_path = '/applications'
        app = TestApp(base_app)
        headers = {'x-appenlight-auth-token': ''}
        app.post_json(url_path,
                      params={'resource_name': 'user_foo'},
                      headers=headers, status=403)

    def test_create_application_proper(self, base_app):
        url_path = '/applications'
        app = TestApp(base_app)
        headers = {'x-appenlight-auth-token': '1234'}
        app.post_json(url_path,
                      params={'resource_name': 'user_foo'},
                      headers=headers, status=200)
