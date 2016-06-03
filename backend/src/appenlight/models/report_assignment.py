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

from ziggurat_foundations.models.base import BaseModel
from appenlight.models import Base
import sqlalchemy as sa


class ReportAssignment(Base, BaseModel):
    __tablename__ = 'reports_assignments'

    group_id = sa.Column(sa.BigInteger,
                         sa.ForeignKey('reports_groups.id', ondelete='cascade',
                                       onupdate='cascade'),
                         primary_key=True)
    owner_id = sa.Column(sa.Integer,
                          sa.ForeignKey('users.id', onupdate='CASCADE',
                                        ondelete='CASCADE'), primary_key=True)
    report_time = sa.Column(sa.DateTime(), nullable=False)
