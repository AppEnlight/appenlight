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
import sqlalchemy as sa

from appenlight.models import Base
from appenlight.models.report_group import ReportGroup


class ApplicationPostprocessConf(Base, BaseModel):
    """
    Stores prioritizing conditions for reports
    This is later used for rule parsing like "if 10 occurences bump priority +1"
    """

    __tablename__ = 'application_postprocess_conf'

    pkey = sa.Column(sa.Integer(), nullable=False, primary_key=True)
    resource_id = sa.Column(sa.Integer(),
                            sa.ForeignKey('resources.resource_id',
                                          onupdate='CASCADE',
                                          ondelete='CASCADE'))
    do = sa.Column(sa.Unicode(25), nullable=False)
    new_value = sa.Column(sa.UnicodeText(), nullable=False, default='')
    rule = sa.Column(sa.dialects.postgresql.JSON,
                     nullable=False, default={'field': 'http_status',
                                              "op": "ge", "value": "500"})

    def postprocess(self, item):
        new_value = int(self.new_value)
        item.priority = ReportGroup.priority + new_value
