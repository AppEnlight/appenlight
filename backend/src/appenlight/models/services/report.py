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

import logging
import sqlalchemy as sa

from appenlight.models import get_db_session
from appenlight.models.report import Report
from appenlight.models.report_stat import ReportStat
from appenlight.models.services.base import BaseService

log = logging.getLogger(__name__)


class ReportService(BaseService):
    @classmethod
    def by_app_ids(cls, app_ids=None, order_by=True, db_session=None):
        db_session = get_db_session(db_session)
        q = db_session.query(Report)
        if app_ids:
            q = q.filter(Report.resource_id.in_(app_ids))
        if order_by:
            q = q.order_by(sa.desc(Report.id))
        return q

    @classmethod
    def generate_stat_rows(cls, report, resource, report_group, occurences=1,
                           db_session=None):
        """
        Generates timeseries for this report's group
        """
        db_session = get_db_session(db_session)
        stats = ReportStat(resource_id=report.resource_id,
                           group_id=report_group.id,
                           start_interval=report.start_time,
                           owner_user_id=resource.owner_user_id,
                           server_name=report.tags.get('server_name'),
                           view_name=report.tags.get('view_name'),
                           type=report.report_type,
                           occurences=occurences,
                           duration=report.duration)
        db_session.add(stats)
        db_session.flush()
        return stats
