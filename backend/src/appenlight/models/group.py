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
