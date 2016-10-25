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

from appenlight.models import Base, DBSession


@pytest.fixture
def base_app(request):
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
def clean_tables():
    tables = Base.metadata.tables.keys()
    transaction.begin()
    for t in tables:
        if not t.startswith('alembic_'):
            DBSession.execute('truncate %s cascade' % t)
    session = DBSession()
    mark_changed(session)
    transaction.commit()


@pytest.fixture
def default_user():
    from appenlight.models.user import User
    from appenlight.models.auth_token import AuthToken
    transaction.begin()
    user = User(id=1,
                user_name='testuser',
                status=1,
                email='foo@barbaz99.com')
    DBSession.add(user)
    token = AuthToken(token='1234')
    user.auth_tokens.append(token)
    DBSession.flush()
    transaction.commit()
    return user


@pytest.fixture
def default_application(default_user):
    from appenlight.models.application import Application

    transaction.begin()
    application = Application(
        resource_id=1, resource_name='testapp', api_key='xxxx')
    DBSession.add(application)
    default_user.resources.append(application)
    DBSession.flush()
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
