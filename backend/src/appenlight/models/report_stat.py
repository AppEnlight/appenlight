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

import sqlalchemy as sa

from appenlight.lib.enums import ReportType
from appenlight.models import Base
from ziggurat_foundations.models.base import BaseModel


class ReportStat(Base, BaseModel):
    __tablename__ = 'reports_stats'
    __table_args__ = {'implicit_returning': False}

    group_id = sa.Column(sa.BigInteger(),
                         sa.ForeignKey('reports_groups.id'),
                         nullable=False)
    resource_id = sa.Column(sa.Integer(),
                            sa.ForeignKey('applications.resource_id'),
                            nullable=False)
    start_interval = sa.Column(sa.DateTime(), nullable=False)
    occurences = sa.Column(sa.Integer, nullable=True, default=0)
    owner_user_id = sa.Column(sa.Integer(), sa.ForeignKey('users.id'),
                              nullable=True)
    type = sa.Column(sa.Integer, nullable=True, default=0)
    duration = sa.Column(sa.Float, nullable=True, default=0)
    id = sa.Column(sa.BigInteger, nullable=False, primary_key=True)
    server_name = sa.Column(sa.Unicode(128), nullable=False, default='')
    view_name = sa.Column(sa.Unicode(128), nullable=False, default='')

    @property
    def partition_id(self):
        return 'rcae_r_%s' % self.start_interval.strftime('%Y_%m')

    def es_doc(self):
        return {
            'resource_id': self.resource_id,
            'timestamp': self.start_interval,
            'pg_id': str(self.id),
            'permanent': True,
            'request_id': None,
            'log_level': 'ERROR',
            'message': None,
            'namespace': 'appenlight.error',
            'tags': {
                'duration': {'values': self.duration,
                             'numeric_values': self.duration},
                'occurences': {'values': self.occurences,
                               'numeric_values': self.occurences},
                'group_id': {'values': self.group_id,
                             'numeric_values': self.group_id},
                'type': {'values': ReportType.key_from_value(self.type),
                         'numeric_values': self.type},
                'server_name': {'values': self.server_name,
                                'numeric_values': None},
                'view_name': {'values': self.view_name,
                              'numeric_values': None},
            },
            'tag_list': ['duration', 'occurences', 'group_id', 'type',
                         'server_name', 'view_name']
        }
