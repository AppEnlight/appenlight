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

from ziggurat_foundations.models.group import GroupMixin
from appenlight.models import Base


class Group(GroupMixin, Base):
    __possible_permissions__ = ('root_administration',
                                'test_features',
                                'admin_panel',
                                'admin_users',
                                'manage_partitions',)

    def get_dict(self, exclude_keys=None, include_keys=None,
                 include_perms=False):
        result = super(Group, self).get_dict(exclude_keys, include_keys)
        if include_perms:
            result['possible_permissions'] = self.__possible_permissions__
            result['current_permissions'] = [p.perm_name for p in
                                             self.permissions]
        else:
            result['possible_permissions'] = []
            result['current_permissions'] = []
        exclude_keys_list = exclude_keys or []
        include_keys_list = include_keys or []
        d = {}
        for k in result.keys():
            if (k not in exclude_keys_list and
                    (k in include_keys_list or not include_keys)):
                d[k] = result[k]
        return d
