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

from appenlight.models.group_resource_permission import GroupResourcePermission
from appenlight.models import get_db_session
from ziggurat_foundations.models.services.group_resource_permission import (
    GroupResourcePermissionService,
)


class GroupResourcePermissionService(GroupResourcePermissionService):
    @classmethod
    def by_resource_group_and_perm(
        cls, group_id, perm_name, resource_id, db_session=None
    ):
        """ return all instances by user name, perm name and resource id """
        db_session = get_db_session(db_session)
        query = db_session.query(GroupResourcePermission)
        query = query.filter(GroupResourcePermission.group_id == group_id)
        query = query.filter(GroupResourcePermission.resource_id == resource_id)
        query = query.filter(GroupResourcePermission.perm_name == perm_name)
        return query.first()
