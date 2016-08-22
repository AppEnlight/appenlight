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

from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON

from ziggurat_foundations.models.base import BaseModel
from appenlight.lib.utils import convert_es_type
from appenlight.models import Base


class Metric(Base, BaseModel):
    __tablename__ = 'metrics'
    __table_args__ = {'implicit_returning': False}

    pkey = sa.Column(sa.BigInteger(), primary_key=True)
    resource_id = sa.Column(sa.Integer(),
                            sa.ForeignKey('applications.resource_id'),
                            nullable=False, primary_key=True)
    timestamp = sa.Column(sa.DateTime(), default=datetime.utcnow,
                          server_default=sa.func.now())
    tags = sa.Column(JSON(), default={})
    namespace = sa.Column(sa.Unicode(255))

    @property
    def partition_id(self):
        return 'rcae_m_%s' % self.timestamp.strftime('%Y_%m_%d')

    def es_doc(self):
        tags = {}
        tag_list = []
        for name, value in self.tags.items():
            # replace dot in indexed tag name
            name = name.replace('.', '_')
            tag_list.append(name)
            tags[name] = {
                "values": convert_es_type(value),
                "numeric_values": value if (
                    isinstance(value, (int, float)) and
                    not isinstance(value, bool)) else None
            }

        return {
            'resource_id': self.resource_id,
            'timestamp': self.timestamp,
            'namespace': self.namespace,
            'tags': tags,
            'tag_list': tag_list
        }
