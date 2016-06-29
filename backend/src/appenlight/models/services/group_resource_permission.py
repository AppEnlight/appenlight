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
# AppEnlight Enterprise Edition, including its added features, Support
# services, and proprietary license terms, please see
# https://rhodecode.com/licenses/

from appenlight.models.group_resource_permission import GroupResourcePermission
from appenlight.models import get_db_session
from appenlight.models.services.base import BaseService


class GroupResourcePermissionService(BaseService):
    @classmethod
    def by_resource_group_and_perm(cls, group_id, perm_name, resource_id,
                                   db_session=None):
        """ return all instances by user name, perm name and resource id """
        db_session = get_db_session(db_session)
        query = db_session.query(GroupResourcePermission)
        query = query.filter(GroupResourcePermission.group_id == group_id)
        query = query.filter(
            GroupResourcePermission.resource_id == resource_id)
        query = query.filter(GroupResourcePermission.perm_name == perm_name)
        return query.first()
