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
