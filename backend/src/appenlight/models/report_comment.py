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
