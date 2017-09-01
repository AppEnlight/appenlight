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
