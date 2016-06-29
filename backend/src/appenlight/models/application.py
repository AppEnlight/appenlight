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
