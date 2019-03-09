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

import mock
import os
import pytest
import transaction
from datetime import datetime

from alembic.config import Config
from alembic import command
from collections import OrderedDict
from zope.sqlalchemy import mark_changed
from pyramid.paster import get_appsettings
from pyramid import testing


@pytest.fixture
def base_app(request, mocker):
    # disable email sending
    mocker.patch('pyramid_mailer.mailer_factory_from_settings', mocker.Mock())

    from appenlight import main
    import transaction
    current_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(current_dir, '../../../../',
                        os.environ.get("APPENLIGHT_INI", 'testing.ini'))
    # appsettings from ini
    app_settings = get_appsettings(path, name="appenlight")
    app = main({}, **app_settings)
    app_request = testing.DummyRequest(base_url='https://appenlight.com')
    app_request.tm = transaction.manager
    app_request.add_flash_to_headers = mock.Mock()
    testing.setUp(registry=app.registry, request=app_request)

    def teardown():
        testing.tearDown()

    request.addfinalizer(teardown)

    return app


@pytest.fixture
def with_migrations(request, base_app):
    settings = base_app.registry.settings
    alembic_cfg = Config()
    alembic_cfg.set_main_option("script_location",
                                "ziggurat_foundations:migrations")
    alembic_cfg.set_main_option("sqlalchemy.url", settings["sqlalchemy.url"])
    command.upgrade(alembic_cfg, "head")
    alembic_cfg = Config()
    alembic_cfg.set_main_option("script_location", "appenlight:migrations")
    alembic_cfg.set_main_option("sqlalchemy.url", settings["sqlalchemy.url"])
    command.upgrade(alembic_cfg, "head")

    for plugin_name, config in base_app.registry.appenlight_plugins.items():
        if config['sqlalchemy_migrations']:
            alembic_cfg = Config()
            alembic_cfg.set_main_option("script_location",
                                        config['sqlalchemy_migrations'])
            alembic_cfg.set_main_option(
                "sqlalchemy.url",
                base_app.registry.settings["sqlalchemy.url"])
            command.upgrade(alembic_cfg, "head")


@pytest.fixture
def default_data(base_app):
    from appenlight.models.services.config import ConfigService
    from appenlight.lib import get_callable
    transaction.begin()
    ConfigService.setup_default_values()
    for plugin_name, config in base_app.registry.appenlight_plugins.items():
        if config['default_values_setter']:
            get_callable(config['default_values_setter'])()
    transaction.commit()


@pytest.fixture
def clean_tables(request):
    from appenlight.models import Base, DBSession

    def fin():
        tables = Base.metadata.tables.keys()
        transaction.begin()
        for t in tables:
            if not t.startswith('alembic_'):
                DBSession.execute('truncate %s cascade' % t)
        session = DBSession()
        mark_changed(session)
        transaction.commit()

    request.addfinalizer(fin)


@pytest.fixture
def default_user():
    from appenlight.models import DBSession
    from appenlight.models.user import User
    from appenlight.models.auth_token import AuthToken
    transaction.begin()
    session = DBSession()
    user = User(id=1,
                user_name='testuser',
                status=1,
                email='foo@barbaz99.com')
    session.add(user)
    token = AuthToken(token='1234')
    user.auth_tokens.append(token)
    session.execute("SELECT nextval('users_id_seq')")
    transaction.commit()
    return user


@pytest.fixture
def default_application(default_user):
    from appenlight.models import DBSession
    from appenlight.models.application import Application

    transaction.begin()
    session = DBSession()
    application = Application(
        resource_id=1, resource_name='testapp', api_key='xxxx')
    session.add(application)
    default_user.resources.append(application)
    session.execute("SELECT nextval('resources_resource_id_seq')")
    transaction.commit()
    return application


@pytest.fixture
def report_type_matrix():
    from appenlight.models.report import REPORT_TYPE_MATRIX
    return REPORT_TYPE_MATRIX


@pytest.fixture
def chart_series():
    series = []

    for x in range(1, 7):
        tmp_list = [('key', 'X'), ('0_1', x)]
        if x % 2 == 0:
            tmp_list.append(('0_2', x))
        if x % 3 == 0:
            tmp_list.append(('0_3', x))

        series.append(
            OrderedDict(tmp_list)
        )
    return series


@pytest.fixture
def log_schema():
    from appenlight.validators import LogListSchema
    schema = LogListSchema().bind(utcnow=datetime.utcnow())
    return schema

@pytest.fixture
def general_metrics_schema():
    from appenlight.validators import GeneralMetricsListSchema
    schema = GeneralMetricsListSchema().bind(utcnow=datetime.utcnow())
    return schema

@pytest.fixture
def request_metrics_schema():
    from appenlight.validators import MetricsListSchema
    schema = MetricsListSchema().bind(utcnow=datetime.utcnow())
    return schema

@pytest.fixture
def report_05_schema():
    from appenlight.validators import ReportListSchema_0_5
    schema = ReportListSchema_0_5().bind(utcnow=datetime.utcnow())
    return schema
