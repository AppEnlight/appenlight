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

import uuid
import logging
import sqlalchemy as sa
from appenlight.models.resource import Resource
from sqlalchemy.orm import aliased

log = logging.getLogger(__name__)


def generate_api_key():
    uid = str(uuid.uuid4()).replace('-', '')
    return uid[0:32]


class Application(Resource):
    """
    Resource of application type
    """

    __tablename__ = 'applications'
    __mapper_args__ = {'polymorphic_identity': 'application'}

    # lists configurable possible permissions for this resource type
    __possible_permissions__ = ('view', 'update_reports')

    resource_id = sa.Column(sa.Integer(),
                            sa.ForeignKey('resources.resource_id',
                                          onupdate='CASCADE',
                                          ondelete='CASCADE', ),
                            primary_key=True, )
    domains = sa.Column(sa.UnicodeText(), nullable=False, default='')
    api_key = sa.Column(sa.String(32), nullable=False, unique=True, index=True,
                        default=generate_api_key)
    public_key = sa.Column(sa.String(32), nullable=False, unique=True,
                           index=True,
                           default=generate_api_key)
    default_grouping = sa.Column(sa.Unicode(20), nullable=False,
                                 default='url_traceback')
    error_report_threshold = sa.Column(sa.Integer(), default=10)
    slow_report_threshold = sa.Column(sa.Integer(), default=10)
    allow_permanent_storage = sa.Column(sa.Boolean(), default=False,
                                        nullable=False)

    @sa.orm.validates('default_grouping')
    def validate_default_grouping(self, key, grouping):
        """ validate if resouce can have specific permission """
        assert grouping in ['url_type', 'url_traceback', 'traceback_server']
        return grouping

    report_groups = sa.orm.relationship('ReportGroup',
                                        cascade="all, delete-orphan",
                                        passive_deletes=True,
                                        passive_updates=True,
                                        lazy='dynamic',
                                        backref=sa.orm.backref('application',
                                                               lazy="joined"))

    postprocess_conf = sa.orm.relationship('ApplicationPostprocessConf',
                                           cascade="all, delete-orphan",
                                           passive_deletes=True,
                                           passive_updates=True,
                                           backref='resource')

    logs = sa.orm.relationship('Log',
                               lazy='dynamic',
                               backref='application',
                               passive_deletes=True,
                               passive_updates=True, )

    integrations = sa.orm.relationship('IntegrationBase',
                                       backref='resource',
                                       cascade="all, delete-orphan",
                                       passive_deletes=True,
                                       passive_updates=True, )

    def generate_api_key(self):
        return generate_api_key()


def after_update(mapper, connection, target):
    from appenlight.models.services.application import ApplicationService
    log.info('clearing out ApplicationService cache')
    ApplicationService.by_id_cached().invalidate(target.resource_id)
    ApplicationService.by_api_key_cached().invalidate(target.api_key)


sa.event.listen(Application, 'after_update', after_update)
sa.event.listen(Application, 'after_delete', after_update)
