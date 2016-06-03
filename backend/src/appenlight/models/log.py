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

import sqlalchemy as sa
import logging
import hashlib

from datetime import datetime
from appenlight.models import Base
from appenlight.lib.utils import convert_es_type
from appenlight.lib.enums import LogLevel
from sqlalchemy.dialects.postgresql import JSON
from ziggurat_foundations.models.base import BaseModel

log = logging.getLogger(__name__)


class Log(Base, BaseModel):
    __tablename__ = 'logs'
    __table_args__ = {'implicit_returning': False}

    log_id = sa.Column(sa.BigInteger(), nullable=False, primary_key=True)
    resource_id = sa.Column(sa.Integer(),
                            sa.ForeignKey('applications.resource_id',
                                          onupdate='CASCADE',
                                          ondelete='CASCADE'),
                            nullable=False,
                            index=True)
    log_level = sa.Column(sa.Unicode, nullable=False, index=True,
                          default='INFO')
    message = sa.Column(sa.UnicodeText(), default='')
    timestamp = sa.Column(sa.DateTime(), default=datetime.utcnow,
                          server_default=sa.func.now())
    request_id = sa.Column(sa.Unicode())
    namespace = sa.Column(sa.Unicode())
    primary_key = sa.Column(sa.Unicode())

    tags = sa.Column(JSON(), default={})
    permanent = sa.Column(sa.Boolean(), nullable=False, default=False)

    def __str__(self):
        return self.__unicode__().encode('utf8')

    def __unicode__(self):
        return '<Log id:%s, lv:%s, ns:%s >' % (
            self.log_id, self.log_level, self.namespace)

    def set_data(self, data, resource):
        level = data.get('log_level').upper()
        self.log_level = getattr(LogLevel, level, LogLevel.UNKNOWN)
        self.message = data.get('message', '')
        server_name = data.get('server', '').lower() or 'unknown'
        self.tags = {
            'server_name': server_name
        }
        if data.get('tags'):
            for tag_tuple in data['tags']:
                self.tags[tag_tuple[0]] = tag_tuple[1]
        self.timestamp = data['date']
        r_id = data.get('request_id', '')
        if not r_id:
            r_id = ''
        self.request_id = r_id.replace('-', '')
        self.resource_id = resource.resource_id
        self.namespace = data.get('namespace') or ''
        self.permanent = data.get('permanent')
        self.primary_key = data.get('primary_key')
        if self.primary_key is not None:
            self.tags['appenlight_primary_key'] = self.primary_key

    def get_dict(self):
        instance_dict = super(Log, self).get_dict()
        instance_dict['log_level'] = LogLevel.key_from_value(self.log_level)
        instance_dict['resource_name'] = self.application.resource_name
        return instance_dict

    @property
    def delete_hash(self):
        if not self.primary_key:
            return None

        to_hash = '{}_{}_{}'.format(self.resource_id, self.primary_key,
                                     self.namespace)
        return hashlib.sha1(to_hash.encode('utf8')).hexdigest()

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
            'pg_id': str(self.log_id),
            'delete_hash': self.delete_hash,
            'resource_id': self.resource_id,
            'request_id': self.request_id,
            'log_level': LogLevel.key_from_value(self.log_level),
            'timestamp': self.timestamp,
            'message': self.message if self.message else '',
            'namespace': self.namespace if self.namespace else '',
            'tags': tags,
            'tag_list': tag_list
        }

    @property
    def partition_id(self):
        if self.permanent:
            return 'rcae_l_%s' % self.timestamp.strftime('%Y_%m')
        else:
            return 'rcae_l_%s' % self.timestamp.strftime('%Y_%m_%d')
