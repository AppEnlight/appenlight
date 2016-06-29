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

import logging

from datetime import datetime, timedelta
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPUnprocessableEntity

from appenlight.models import DBSession
from appenlight.models.user import User
from appenlight.models.report_comment import ReportComment
from appenlight.models.report_assignment import ReportAssignment
from appenlight.models.services.user import UserService
from appenlight.models.services.report_group import ReportGroupService
from appenlight import forms
from appenlight.lib.enums import ReportType
from appenlight.lib.helpers import gen_pagination_headers
from appenlight.lib.utils import build_filter_settings_from_query_dict
from appenlight.validators import ReportSearchSchema, TagListSchema, \
    accepted_search_params
from webob.multidict import MultiDict

_ = str

log = logging.getLogger(__name__)

section_filters_key = 'appenlight:reports:filter:%s'


@view_config(route_name='reports', renderer='json', permission='authenticated')
@view_config(route_name='slow_reports', renderer='json',
             permission='authenticated')
def index(request):
    """
    Returns list of report groups based on user search query
    """
    if request.user:
        request.user.last_login_date = datetime.utcnow()

    applications = request.user.resources_with_perms(
        ['view'], resource_types=['application'])

    search_params = request.GET.mixed()

    all_possible_app_ids = set([app.resource_id for app in applications])
    schema = ReportSearchSchema().bind(resources=all_possible_app_ids)
    tag_schema = TagListSchema()
    filter_settings = schema.deserialize(search_params)
    tag_list = [{"name": k, "value": v} for k, v in filter_settings.items()
                if k not in accepted_search_params]
    tags = tag_schema.deserialize(tag_list)
    filter_settings['tags'] = tags
    if request.matched_route.name == 'slow_reports':
        filter_settings['report_type'] = [ReportType.slow]
    else:
        filter_settings['report_type'] = [ReportType.error]

    reports_paginator = ReportGroupService.get_paginator_by_app_ids(
        app_ids=filter_settings['resource'],
        page=filter_settings['page'],
        filter_settings=filter_settings
    )
    reports = []
    include_keys = ('id', 'http_status', 'report_type', 'resource_name',
                    'front_url', 'resource_id', 'error', 'url_path', 'tags',
                    'duration')
    for report in reports_paginator.sa_items:
        reports.append(report.get_dict(request, include_keys=include_keys))
    headers = gen_pagination_headers(request, reports_paginator)
    request.response.headers.update(headers)
    return reports


@view_config(route_name='report_groups', renderer='json', permission='view',
             request_method="GET")
def view_report(request):
    """
    Show individual detailed report group along with latest report
    """
    report_group = request.context.report_group
    if not report_group.read:
        report_group.read = True

    report_id = request.params.get('reportId', request.params.get('report_id'))
    report_dict = report_group.get_report(report_id).get_dict(request,
                                                              details=True)
    # disallow browsing other occurences by anonymous
    if not request.user:
        report_dict.pop('group_next_report', None)
        report_dict.pop('group_previous_report', None)
    return report_dict


@view_config(route_name='report_groups', renderer='json',
             permission='update_reports', request_method='DELETE')
def remove(request):
    """
    Used to remove reourt groups from database
    """
    report = request.context.report_group
    form = forms.ReactorForm(request.POST, csrf_context=request)
    form.validate()
    DBSession.delete(report)
    return True


@view_config(route_name='report_groups_property', match_param='key=comments',
             renderer='json', permission='view', request_method="POST")
def comment_create(request):
    """
    Creates user comments for report group, sends email notifications
    of said comments
    """
    report_group = request.context.report_group
    application = request.context.resource
    form = forms.CommentForm(MultiDict(request.unsafe_json_body),
                             csrf_context=request)
    if request.method == 'POST' and form.validate():
        comment = ReportComment(owner_id=request.user.id,
                                report_time=report_group.first_timestamp)
        form.populate_obj(comment)
        report_group.comments.append(comment)
        perm_list = application.users_for_perm('view')
        uids_to_notify = []
        users_to_notify = []
        for perm in perm_list:
            user = perm.user
            if ('@{}'.format(user.user_name) in comment.body and
                        user.id not in uids_to_notify):
                uids_to_notify.append(user.id)
                users_to_notify.append(user)

        commenters = ReportGroupService.users_commenting(
            report_group, exclude_user_id=request.user.id)
        for user in commenters:
            if user.id not in uids_to_notify:
                uids_to_notify.append(user.id)
                users_to_notify.append(user)

        for user in users_to_notify:
            email_vars = {'user': user,
                          'commenting_user': request.user,
                          'request': request,
                          'application': application,
                          'report_group': report_group,
                          'comment': comment,
                          'email_title': "AppEnlight :: New comment"}
            UserService.send_email(
                request,
                recipients=[user.email],
                variables=email_vars,
                template='/email_templates/new_comment_report.jinja2')
        request.session.flash(_('Your comment was created'))
        return comment.get_dict()
    else:
        return form.errors


@view_config(route_name='report_groups_property',
             match_param='key=assigned_users', renderer='json',
             permission='update_reports', request_method="GET")
def assigned_users(request):
    """
    Returns list of users a specific report group is assigned for review
    """
    report_group = request.context.report_group
    application = request.context.resource
    users = set([p.user for p in application.users_for_perm('view')])
    currently_assigned = [u.user_name for u in report_group.assigned_users]
    user_status = {'assigned': [], 'unassigned': []}
    # handle users
    for user in users:
        user_dict = {'user_name': user.user_name,
                     'gravatar_url': user.gravatar_url(),
                     'name': '%s %s' % (user.first_name, user.last_name,)}
        if user.user_name in currently_assigned:
            user_status['assigned'].append(user_dict)
        elif user_dict not in user_status['unassigned']:
            user_status['unassigned'].append(user_dict)
    return user_status


@view_config(route_name='report_groups_property',
             match_param='key=assigned_users', renderer='json',
             permission='update_reports', request_method="PATCH")
def assign_users(request):
    """
    Assigns specific report group to user for review - send email notification
    """
    report_group = request.context.report_group
    application = request.context.resource
    currently_assigned = [u.user_name for u in report_group.assigned_users]
    new_assigns = request.unsafe_json_body

    # first unassign old users
    for user_name in new_assigns['unassigned']:
        if user_name in currently_assigned:
            user = User.by_user_name(user_name)
            report_group.assigned_users.remove(user)
            comment = ReportComment(owner_id=request.user.id,
                                    report_time=report_group.first_timestamp)
            comment.body = 'Unassigned group from @%s' % user_name
            report_group.comments.append(comment)

    # assign new users
    for user_name in new_assigns['assigned']:
        if user_name not in currently_assigned:
            user = User.by_user_name(user_name)
            if user in report_group.assigned_users:
                report_group.assigned_users.remove(user)
            DBSession.flush()
            assignment = ReportAssignment(
                owner_id=user.id,
                report_time=report_group.first_timestamp,
                group_id=report_group.id)
            DBSession.add(assignment)

            comment = ReportComment(owner_id=request.user.id,
                                    report_time=report_group.first_timestamp)
            comment.body = 'Assigned report_group to @%s' % user_name
            report_group.comments.append(comment)

            email_vars = {'user': user,
                          'request': request,
                          'application': application,
                          'report_group': report_group,
                          'email_title': "AppEnlight :: Assigned Report"}
            UserService.send_email(request, recipients=[user.email],
                                   variables=email_vars,
                                   template='/email_templates/assigned_report.jinja2')

    return True


@view_config(route_name='report_groups_property', match_param='key=history',
             renderer='json', permission='view')
def history(request):
    """ Separate error graph or similar graph"""
    report_group = request.context.report_group
    query_params = request.GET.mixed()
    query_params['resource'] = (report_group.resource_id,)

    filter_settings = build_filter_settings_from_query_dict(request,
                                                            query_params)
    if not filter_settings.get('end_date'):
        end_date = datetime.utcnow().replace(microsecond=0, second=0)
        filter_settings['end_date'] = end_date

    if not filter_settings.get('start_date'):
        delta = timedelta(days=30)
        filter_settings['start_date'] = filter_settings['end_date'] - delta

    filter_settings['group_id'] = report_group.id

    result = ReportGroupService.get_report_stats(request, filter_settings)

    plot_data = []
    for row in result:
        point = {
            'x': row['x'],
            'reports': row['report'] + row['slow_report'] + row['not_found']}
        plot_data.append(point)

    return plot_data


@view_config(route_name='report_groups', renderer='json',
             permission='update_reports', request_method="PATCH")
def report_groups_PATCH(request):
    """
    Used to update the report group fixed status
    """
    report_group = request.context.report_group
    allowed_keys = ['public', 'fixed']
    for k, v in request.unsafe_json_body.items():
        if k in allowed_keys:
            setattr(report_group, k, v)
        else:
            return HTTPUnprocessableEntity()
    return report_group.get_dict(request)
