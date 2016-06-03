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

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import MetaData
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension
import ziggurat_foundations
from ziggurat_foundations.models.base import get_db_session

log = logging.getLogger(__name__)

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))

NAMING_CONVENTION = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=NAMING_CONVENTION)
Base = declarative_base(metadata=metadata)

# optional for request.db approach
ziggurat_foundations.models.DBSession = DBSession


class Datastores(object):
    redis = None
    es = None


def register_datastores(es_conn, redis_conn, redis_lockmgr):
    Datastores.es = es_conn
    Datastores.redis = redis_conn
    Datastores.lockmgr = redis_lockmgr


class SliceableESQuery(object):
    def __init__(self, query, sort_query=None, aggregations=False, **kwconfig):
        self.query = query
        self.sort_query = sort_query
        self.aggregations = aggregations
        self.items_per_page = kwconfig.pop('items_per_page', 10)
        self.page = kwconfig.pop('page', 1)
        self.kwconfig = kwconfig
        self.result = None

    def __getitem__(self, index):
        config = self.kwconfig.copy()
        config['es_from'] = index.start
        query = self.query.copy()
        if self.sort_query:
            query.update(self.sort_query)
        self.result = Datastores.es.search(query, size=self.items_per_page,
                                           **config)
        if self.aggregations:
            self.items = self.result.get('aggregations')
        else:
            self.items = self.result['hits']['hits']

        return self.items

    def __iter__(self):
        return self.result

    def __len__(self):
        config = self.kwconfig.copy()
        query = self.query.copy()
        self.result = Datastores.es.search(query, size=self.items_per_page,
                                           **config)
        if self.aggregations:
            self.items = self.result.get('aggregations')
        else:
            self.items = self.result['hits']['hits']

        count = int(self.result['hits']['total'])
        return count if count < 5000 else 5000


from appenlight.models.resource import Resource
from appenlight.models.application import Application
from appenlight.models.user import User
from appenlight.models.alert_channel import AlertChannel
from appenlight.models.alert_channel_action import AlertChannelAction
from appenlight.models.request_metric import Metric
from appenlight.models.application_postprocess_conf import \
    ApplicationPostprocessConf
from appenlight.models.auth_token import AuthToken
from appenlight.models.event import Event
from appenlight.models.external_identity import ExternalIdentity
from appenlight.models.group import Group
from appenlight.models.group_permission import GroupPermission
from appenlight.models.group_resource_permission import GroupResourcePermission
from appenlight.models.log import Log
from appenlight.models.plugin_config import PluginConfig
from appenlight.models.report import Report
from appenlight.models.report_group import ReportGroup
from appenlight.models.report_comment import ReportComment
from appenlight.models.report_assignment import ReportAssignment
from appenlight.models.report_stat import ReportStat
from appenlight.models.slow_call import SlowCall
from appenlight.models.tag import Tag
from appenlight.models.user_group import UserGroup
from appenlight.models.user_permission import UserPermission
from appenlight.models.user_resource_permission import UserResourcePermission
from ziggurat_foundations import ziggurat_model_init

ziggurat_model_init(User, Group, UserGroup, GroupPermission, UserPermission,
                    UserResourcePermission, GroupResourcePermission,
                    Resource,
                    ExternalIdentity, passwordmanager=None)
