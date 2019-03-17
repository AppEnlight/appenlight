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

import sqlalchemy as sa
from appenlight.models import Base
from appenlight.lib.utils import permission_tuple_to_dict
from pyramid.security import Allow, ALL_PERMISSIONS
from ziggurat_foundations.models.resource import ResourceMixin
from ziggurat_foundations.models.services.resource import ResourceService


class Resource(ResourceMixin, Base):
    events = sa.orm.relationship(
        "Event",
        lazy="dynamic",
        backref="resource",
        passive_deletes=True,
        passive_updates=True,
    )

    @property
    def owner_user_name(self):
        if self.owner:
            return self.owner.user_name

    @property
    def owner_group_name(self):
        if self.owner_group:
            return self.owner_group.group_name

    def get_dict(
        self,
        exclude_keys=None,
        include_keys=None,
        include_perms=False,
        include_processing_rules=False,
    ):
        result = super(Resource, self).get_dict(exclude_keys, include_keys)
        result["possible_permissions"] = self.__possible_permissions__
        if include_perms:
            result["current_permissions"] = self.user_permissions_list
        else:
            result["current_permissions"] = []
        if include_processing_rules:
            result["postprocessing_rules"] = [
                rule.get_dict() for rule in self.postprocess_conf
            ]
        else:
            result["postprocessing_rules"] = []
        exclude_keys_list = exclude_keys or []
        include_keys_list = include_keys or []
        d = {}
        for k in result.keys():
            if k not in exclude_keys_list and (
                k in include_keys_list or not include_keys
            ):
                d[k] = result[k]
        for k in ["owner_user_name", "owner_group_name"]:
            if k not in exclude_keys_list and (
                k in include_keys_list or not include_keys
            ):
                d[k] = getattr(self, k)
        return d

    @property
    def user_permissions_list(self):
        return [
            permission_tuple_to_dict(perm)
            for perm in ResourceService.users_for_perm(
                self, "__any_permission__", limit_group_permissions=True
            )
        ]

    @property
    def __acl__(self):
        acls = []

        if self.owner_user_id:
            acls.extend([(Allow, self.owner_user_id, ALL_PERMISSIONS)])

        if self.owner_group_id:
            acls.extend([(Allow, "group:%s" % self.owner_group_id, ALL_PERMISSIONS)])
        return acls
