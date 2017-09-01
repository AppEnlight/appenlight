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

    def get_assignees(self, request):
        """Gets list of possible assignees"""
        cache_region = request.registry.cache_regions.redis_sec_30
        @cache_region.cache_on_arguments('JiraClient.get_assignees')
        def cached(project_name):
            users = self.client.search_assignable_users_for_issues(
                None, project=project_name)
            results = []
            for user in users:
                results.append({"id": user.name, "name": user.displayName})
            return results
        return cached(self.project)

    def get_issue_types(self, request):
        metadata = self.get_metadata(request)
        assignees = self.get_assignees(request)
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

    def get_metadata(self, request):
        # cache_region = request.registry.cache_regions.redis_sec_30
        # @cache_region.cache_on_arguments('JiraClient.get_metadata')
        def cached(project_name):
            return self.client.createmeta(
                projectKeys=project_name, expand='projects.issuetypes.fields')
        return cached(self.project)

    def create_issue(self, form_data, request):
        issue_types = self.get_issue_types(request)
        payload = {
            'project': {'key': form_data['project']},
            'summary': form_data['title'],
            'description': form_data['content'],
            'issuetype': {'id': form_data['issue_type']},
            "priority": {'id': form_data['priority']},
            "assignee": {'name': form_data['responsible']},
        }
        for issue_type in issue_types:
            if issue_type['id'] == form_data['issue_type']:
                for field in issue_type['fields']:
                    # set some defaults for other required fields
                    if field == 'reporter':
                        payload["reporter"] = {'id': self.user_name}
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
