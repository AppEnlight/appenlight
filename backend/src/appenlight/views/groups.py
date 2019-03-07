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

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPUnprocessableEntity, HTTPNotFound

from ziggurat_foundations.models.services.user import UserService
from appenlight.lib.utils import permission_tuple_to_dict
from appenlight.models.services.config import ConfigService
from appenlight.models.group import Group
from appenlight.models.services.group import GroupService
from appenlight.models.user import User
from appenlight.models import DBSession
from appenlight import forms
from webob.multidict import MultiDict

log = logging.getLogger(__name__)

_ = str


@view_config(route_name='groups_no_id', renderer='json',
             request_method="GET", permission='authenticated')
def groups_list(request):
    """
    Returns groups list
    """
    groups = Group.all().order_by(Group.group_name)
    list_groups = ConfigService.by_key_and_section(
        'list_groups_to_non_admins', 'global')
    if list_groups.value or request.has_permission('root_administration'):
        return [g.get_dict() for g in groups]
    else:
        return []


@view_config(route_name='groups_no_id', renderer='json',
             request_method="POST", permission='root_administration')
def groups_create(request):
    """
    Returns groups list
    """
    form = forms.GroupCreateForm(
        MultiDict(request.safe_json_body or {}), csrf_context=request)
    if form.validate():
        log.info('registering group')
        group = Group()
        # insert new group here
        DBSession.add(group)
        form.populate_obj(group)
        request.session.flash(_('Group created'))
        DBSession.flush()
        return group.get_dict(include_perms=True)
    else:
        return HTTPUnprocessableEntity(body=form.errors_json)


@view_config(route_name='groups', renderer='json',
             request_method="DELETE", permission='root_administration')
def groups_DELETE(request):
    """
    Removes a groups permanently from db
    """
    msg = _('You cannot remove administrator group from the system')
    group = GroupService.by_id(request.matchdict.get('group_id'))
    if group:
        if group.id == 1:
            request.session.flash(msg, 'warning')
        else:
            DBSession.delete(group)
            request.session.flash(_('Group removed'))
            return True
    request.response.status = 422
    return False


@view_config(route_name='groups', renderer='json',
             request_method="GET", permission='root_administration')
@view_config(route_name='groups', renderer='json',
             request_method="PATCH", permission='root_administration')
def group_update(request):
    """
    Updates group object
    """
    group = GroupService.by_id(request.matchdict.get('group_id'))
    if not group:
        return HTTPNotFound()

    if request.method == 'PATCH':
        form = forms.GroupCreateForm(
            MultiDict(request.unsafe_json_body), csrf_context=request)
        form._modified_group = group
        if form.validate():
            form.populate_obj(group)
        else:
            return HTTPUnprocessableEntity(body=form.errors_json)
    return group.get_dict(include_perms=True)


@view_config(route_name='groups_property',
             match_param='key=resource_permissions',
             renderer='json', permission='root_administration')
def groups_resource_permissions_list(request):
    """
    Get list of permissions assigned to specific resources
    """
    group = GroupService.by_id(request.matchdict.get('group_id'))
    if not group:
        return HTTPNotFound()
    return [permission_tuple_to_dict(perm) for perm in
            GroupService.resources_with_possible_perms(group)]


@view_config(route_name='groups_property',
             match_param='key=users', request_method="GET",
             renderer='json', permission='root_administration')
def groups_users_list(request):
    """
    Get list of permissions assigned to specific resources
    """
    group = GroupService.by_id(request.matchdict.get('group_id'))
    if not group:
        return HTTPNotFound()
    props = ['user_name', 'id', 'first_name', 'last_name', 'email',
             'last_login_date', 'status']
    users_dicts = []
    for user in group.users:
        u_dict = user.get_dict(include_keys=props)
        u_dict['gravatar_url'] = UserService.gravatar_url(user, s=20)
        users_dicts.append(u_dict)
    return users_dicts


@view_config(route_name='groups_property',
             match_param='key=users', request_method="DELETE",
             renderer='json', permission='root_administration')
def groups_users_remove(request):
    """
    Get list of permissions assigned to specific resources
    """
    group = GroupService.by_id(request.matchdict.get('group_id'))
    user = UserService.by_user_name(request.GET.get('user_name'))
    if not group or not user:
        return HTTPNotFound()
    if len(group.users) > 1:
        group.users.remove(user)
        msg = "User removed from group"
        request.session.flash(msg)
        group.member_count = group.users_dynamic.count()
        return True
    msg = "Administrator group needs to contain at least one user"
    request.session.flash(msg, 'warning')
    return False


@view_config(route_name='groups_property',
             match_param='key=users', request_method="POST",
             renderer='json', permission='root_administration')
def groups_users_add(request):
    """
    Get list of permissions assigned to specific resources
    """
    group = GroupService.by_id(request.matchdict.get('group_id'))
    user = UserService.by_user_name(request.unsafe_json_body.get('user_name'))
    if not user:
        user = UserService.by_email(request.unsafe_json_body.get('user_name'))

    if not group or not user:
        return HTTPNotFound()
    if user not in group.users:
        group.users.append(user)
        group.member_count = group.users_dynamic.count()
    props = ['user_name', 'id', 'first_name', 'last_name', 'email',
             'last_login_date', 'status']
    u_dict = user.get_dict(include_keys=props)
    u_dict['gravatar_url'] = UserService.gravatar_url(user, s=20)
    return u_dict
