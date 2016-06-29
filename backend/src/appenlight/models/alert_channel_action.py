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

from appenlight.models.resource import Resource
from appenlight.models import Base, get_db_session
from sqlalchemy.orm import validates
from ziggurat_foundations.models.base import BaseModel


class AlertChannelAction(Base, BaseModel):
    """
    Stores notifications conditions for user's alert channels
    This is later used for rule parsing like "alert if http_status == 500"
    """
    __tablename__ = 'alert_channels_actions'

    types = ['report', 'chart']

    owner_id = sa.Column(sa.Integer,
                         sa.ForeignKey('users.id', onupdate='CASCADE',
                                       ondelete='CASCADE'))
    resource_id = sa.Column(sa.Integer())
    action = sa.Column(sa.Unicode(10), nullable=False, default='always')
    type = sa.Column(sa.Unicode(10), nullable=False)
    other_id = sa.Column(sa.Unicode(40))
    pkey = sa.Column(sa.Integer(), nullable=False, primary_key=True)
    rule = sa.Column(sa.dialects.postgresql.JSON,
                     nullable=False, default={'field': 'http_status',
                                              "op": "ge", "value": "500"})
    config = sa.Column(sa.dialects.postgresql.JSON)
    name = sa.Column(sa.Unicode(255))

    @validates('notify_type')
    def validate_email(self, key, notify_type):
        assert notify_type in ['always', 'only_first']
        return notify_type

    def resource_name(self, db_session=None):
        db_session = get_db_session(db_session)
        if self.resource_id:
            return Resource.by_resource_id(self.resource_id,
                                           db_session=db_session).resource_name
        else:
            return 'any resource'

    def get_dict(self, exclude_keys=None, include_keys=None,
                 extended_info=False):
        """
        Returns dictionary with required information that will be consumed by
        angular
        """
        instance_dict = super(AlertChannelAction, self).get_dict()
        exclude_keys_list = exclude_keys or []
        include_keys_list = include_keys or []
        if extended_info:
            instance_dict['channels'] = [
                c.get_dict(extended_info=False) for c in self.channels]

        d = {}
        for k in instance_dict.keys():
            if (k not in exclude_keys_list and
                    (k in include_keys_list or not include_keys)):
                d[k] = instance_dict[k]
        return d
