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

from datetime import datetime
from appenlight.models import Base
from ziggurat_foundations.models.base import BaseModel


class ReportComment(Base, BaseModel):
    __tablename__ = 'reports_comments'

    comment_id = sa.Column(sa.Integer, nullable=False, primary_key=True)
    group_id = sa.Column(sa.BigInteger,
                         sa.ForeignKey('reports_groups.id', ondelete='cascade',
                                       onupdate='cascade'))
    body = sa.Column(sa.UnicodeText(), default='')
    owner_id = sa.Column(sa.Integer,
                         sa.ForeignKey('users.id', onupdate='CASCADE',
                                       ondelete='CASCADE'))
    created_timestamp = sa.Column(sa.DateTime(),
                                  default=datetime.utcnow,
                                  server_default=sa.func.now())
    report_time = sa.Column(sa.DateTime(), nullable=False)

    owner = sa.orm.relationship('User',
                                lazy='joined')

    @property
    def processed_body(self):
        return self.body

    def get_dict(self):
        instance_dict = super(ReportComment, self).get_dict()
        instance_dict['user_name'] = self.owner.user_name
        return instance_dict
