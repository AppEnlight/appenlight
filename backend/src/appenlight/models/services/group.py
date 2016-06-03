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

from appenlight.models import get_db_session
from appenlight.models.group import Group
from appenlight.models.services.base import BaseService


class GroupService(BaseService):
    @classmethod
    def by_id(cls, group_id, db_session=None):
        db_session = get_db_session(db_session)
        query = db_session.query(Group).filter(Group.id == group_id)
        return query.first()
