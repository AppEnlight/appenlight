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

import sqlalchemy as sa
from appenlight.models import Base
from appenlight.lib.utils import permission_tuple_to_dict
from pyramid.security import Allow, ALL_PERMISSIONS
from ziggurat_foundations.models.resource import ResourceMixin


class Resource(ResourceMixin, Base):
    events = sa.orm.relationship('Event',
                                 lazy='dynamic',
                                 backref='resource',
                                 passive_deletes=True,
                                 passive_updates=True)

    @property
    def owner_user_name(self):
        if self.owner:
            return self.owner.user_name

    @property
    def owner_group_name(self):
        if self.owner_group:
            return self.owner_group.group_name

    def get_dict(self, exclude_keys=None, include_keys=None,
                 include_perms=False, include_processing_rules=False):
        result = super(Resource, self).get_dict(exclude_keys, include_keys)
        result['possible_permissions'] = self.__possible_permissions__
        if include_perms:
            result['current_permissions'] = self.user_permissions_list
        else:
            result['current_permissions'] = []
        if include_processing_rules:
            result["postprocessing_rules"] = [rule.get_dict() for rule
                                              in self.postprocess_conf]
        else:
            result["postprocessing_rules"] = []
        exclude_keys_list = exclude_keys or []
        include_keys_list = include_keys or []
        d = {}
        for k in result.keys():
            if (k not in exclude_keys_list and
                    (k in include_keys_list or not include_keys)):
                d[k] = result[k]
        for k in ['owner_user_name', 'owner_group_name']:
            if (k not in exclude_keys_list and
                    (k in include_keys_list or not include_keys)):
                d[k] = getattr(self, k)
        return d

    @property
    def user_permissions_list(self):
        return [permission_tuple_to_dict(perm) for perm in
                self.users_for_perm('__any_permission__',
                                    limit_group_permissions=True)]

    @property
    def __acl__(self):
        acls = []

        if self.owner_user_id:
            acls.extend([(Allow, self.owner_user_id, ALL_PERMISSIONS,), ])

        if self.owner_group_id:
            acls.extend([(Allow, "group:%s" % self.owner_group_id,
                          ALL_PERMISSIONS,), ])
        return acls
