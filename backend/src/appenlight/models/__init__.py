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
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
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
        self.items_per_page = kwconfig.pop("items_per_page", 10)
        self.page = kwconfig.pop("page", 1)
        self.kwconfig = kwconfig
        self.result = None

    def __getitem__(self, index):
        config = self.kwconfig.copy()
        config["from_"] = index.start
        query = self.query.copy()
        if self.sort_query:
            query.update(self.sort_query)
        self.result = Datastores.es.search(
            body=query, size=self.items_per_page, **config
        )
        if self.aggregations:
            self.items = self.result.get("aggregations")
        else:
            self.items = self.result["hits"]["hits"]

        return self.items

    def __iter__(self):
        return self.result

    def __len__(self):
        config = self.kwconfig.copy()
        query = self.query.copy()
        self.result = Datastores.es.search(
            body=query, size=self.items_per_page, **config
        )
        if self.aggregations:
            self.items = self.result.get("aggregations")
        else:
            self.items = self.result["hits"]["hits"]

        count = int(self.result["hits"]["total"])
        return count if count < 5000 else 5000


from appenlight.models.resource import Resource
from appenlight.models.application import Application
from appenlight.models.user import User
from appenlight.models.alert_channel import AlertChannel
from appenlight.models.alert_channel_action import AlertChannelAction
from appenlight.models.metric import Metric
from appenlight.models.application_postprocess_conf import ApplicationPostprocessConf
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

ziggurat_model_init(
    User,
    Group,
    UserGroup,
    GroupPermission,
    UserPermission,
    UserResourcePermission,
    GroupResourcePermission,
    Resource,
    ExternalIdentity,
    passwordmanager=None,
)
