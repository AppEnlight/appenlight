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
