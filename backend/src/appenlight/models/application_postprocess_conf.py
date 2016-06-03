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
