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

import jira
from appenlight.models.integrations import (IntegrationBase,
                                            IntegrationException)

_ = str


class NotFoundException(Exception):
    pass


class JiraIntegration(IntegrationBase):
    __mapper_args__ = {
        'polymorphic_identity': 'jira'
    }
    front_visible = True
    as_alert_channel = False
    supports_report_alerting = False
    action_notification = True
    integration_action = 'Add issue to Jira'


class JiraClient(object):
    def __init__(self, user_name, password, host_name, project, request=None):
        self.user_name = user_name
        self.password = password
        self.host_name = host_name
        self.project = project
        self.request = request
        try:
            self.client = jira.client.JIRA(options={'server': host_name},
                                           basic_auth=(user_name, password))
        except jira.JIRAError as e:
            raise IntegrationException(
                'Communication problem: HTTP_STATUS:%s, URL:%s ' % (
                    e.status_code, e.url))

    def get_projects(self):
        projects = self.client.projects()
        return projects

    def get_assignees(self):
        """Gets list of possible assignees"""
        users = self.client.search_assignable_users_for_issues(
            None, project=self.project)
        results = []
        for user in users:
            results.append({"id": user.name, "name": user.displayName})
        return results

    def get_metadata(self):
        def cached(project_name):
            metadata = self.client.createmeta(
                projectKeys=project_name, expand='projects.issuetypes.fields')
            assignees = self.get_assignees()
            parsed_metadata = []
            for entry in metadata['projects'][0]['issuetypes']:
                issue = {"name": entry['name'],
                         "id": entry['id'],
                         "fields": []}
                for i_id, field_i in entry['fields'].items():
                    field = {
                        "name": field_i['name'],
                        "id": i_id,
                        "required": field_i['required'],
                        "values": [],
                        "type": field_i['schema'].get('type')
                    }
                    if field_i.get('allowedValues'):
                        field['values'] = []
                        for i in field_i['allowedValues']:
                            field['values'].append(
                                {'id': i['id'],
                                 'name': i.get('name', i.get('value', ''))
                                 })
                    if field['id'] == 'assignee':
                        field['values'] = assignees

                    issue['fields'].append(field)
                parsed_metadata.append(issue)
            return parsed_metadata

        return cached(self.project)

    def create_issue(self, form_data):
        metadata = self.get_metadata()
        payload = {
            'project': {'key': form_data['project']},
            'summary': form_data['title'],
            'description': form_data['content'],
            'issuetype': {'id': '1'},
            "priority": {'id': form_data['priority']},
            "assignee": {'name': form_data['responsible']},
        }
        for issue_type in metadata:
            if issue_type['id'] == '1':
                for field in issue_type['fields']:
                    if field == 'reporter':
                        payload["reporter"] = {'id': self.user_name},
                    if field['required'] and field['id'] not in payload:
                        if field['type'] == 'array':
                            payload[field['id']] = [field['values'][0], ]
                        elif field['type'] == 'string':
                            payload[field['id']] = ''
        new_issue = self.client.create_issue(fields=payload)
        web_url = self.host_name + '/browse/' + new_issue.key
        to_return = {
            'id': new_issue.id,
            'resource_url': new_issue.self,
            'web_url': web_url
        }
        return to_return
