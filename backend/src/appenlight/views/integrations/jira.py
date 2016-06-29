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

import copy
import logging
from appenlight.models.integrations.jira import JiraIntegration, \
    JiraClient, IntegrationException
from appenlight.models.report_comment import ReportComment
from appenlight.models.services.report_group import ReportGroupService
from pyramid.view import view_config
from appenlight import forms
from datetime import datetime
from pyramid.httpexceptions import HTTPFound, HTTPUnprocessableEntity
from webob.multidict import MultiDict

log = logging.getLogger(__name__)

from . import IntegrationView


class JiraView(IntegrationView):
    def create_client(self, form=None):
        """
        Creates a client that can make authenticated requests to jira
        """
        if self.integration and not form:
            user_name = self.integration.config['user_name']
            password = self.integration.config['password']
            host_name = self.integration.config['host_name']
            project = self.integration.config['project']
        else:
            user_name, password = form.user_name.data, form.password.data
            host_name = form.host_name.data
            project = form.host_name.data
        client = JiraClient(user_name, password, host_name, project,
                            request=self.request)
        return client

    @view_config(route_name='integrations_id',
                 match_param=['action=info', 'integration=jira'],
                 renderer='json')
    def get_jira_info(self):
        """
        Get basic metadata - assignees and priority levels from tracker
        """
        try:
            client = self.create_client()
        except IntegrationException as e:
            self.request.response.status_code = 503
            return {'error_messages': [str(e)]}
        assignees = []
        priorities = []
        metadata = client.get_metadata()
        for issue_type in metadata:
            for field in issue_type['fields']:
                if field['id'] == 'assignee':
                    assignees = field['values']
                if field['id'] == 'priority':
                    priorities = field['values']
        return {'assignees': assignees,
                'priorities': priorities}

    @view_config(route_name='integrations_id',
                 match_param=['action=create-issue',
                              'integration=jira'],
                 renderer='json')
    def create_issue(self):
        """
        Creates a new issue in jira from report group
        """
        report = ReportGroupService.by_id(
            self.request.unsafe_json_body['group_id'])
        form_data = {
            'title': self.request.unsafe_json_body.get('title',
                                                       'Unknown Title'),
            'content': self.request.unsafe_json_body.get('content', ''),
            'kind': 'bug',
            'priority': self.request.unsafe_json_body['priority']['id'],
            'responsible': self.request.unsafe_json_body['responsible']['id'],
            'project': self.integration.config['project']
        }
        try:
            client = self.create_client()
            issue = client.create_issue(form_data)
        except IntegrationException as e:
            self.request.response.status_code = 503
            return {'error_messages': [str(e)]}

        comment_body = 'Jira issue created: %s ' % issue['web_url']
        comment = ReportComment(user_name=self.request.user.user_name,
                                report_time=report.first_timestamp,
                                body=comment_body)
        report.comments.append(comment)
        return True

    @view_config(route_name='integrations_id',
                 match_param=['action=setup', 'integration=jira'],
                 renderer='json',
                 permission='edit')
    def setup(self):
        """
        Validates and creates integration between application and jira
        """
        resource = self.request.context.resource
        form = forms.IntegrationJiraForm(
            MultiDict(self.request.safe_json_body or {}),
            csrf_context=self.request, **self.integration_config)
        if self.request.method == 'POST' and form.validate():
            integration_config = {
                'user_name': form.user_name.data,
                'password': form.password.data,
                'host_name': form.host_name.data,
                'project': form.project.data
            }
            if not self.integration:
                # add new integration
                self.integration = JiraIntegration(
                    modified_date=datetime.utcnow(),
                )
                self.request.session.flash('Integration added')
                resource.integrations.append(self.integration)
            else:
                self.request.session.flash('Integration updated')
            self.integration.config = integration_config
            return integration_config
        elif self.request.method == 'POST':
            return HTTPUnprocessableEntity(body=form.errors_json)

        to_return = copy.deepcopy(self.integration_config)
        to_return.pop('password', None)
        return to_return
