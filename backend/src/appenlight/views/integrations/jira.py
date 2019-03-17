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

import copy
import logging
from appenlight.models.integrations.jira import (
    JiraIntegration,
    JiraClient,
    IntegrationException,
)
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
            user_name = self.integration.config["user_name"]
            password = self.integration.config["password"]
            host_name = self.integration.config["host_name"]
            project = self.integration.config["project"]
        else:
            user_name, password = form.user_name.data, form.password.data
            host_name = form.host_name.data
            project = form.host_name.data
        client = JiraClient(
            user_name, password, host_name, project, request=self.request
        )
        return client

    @view_config(
        route_name="integrations_id",
        match_param=["action=info", "integration=jira"],
        renderer="json",
    )
    def get_jira_info(self):
        """
        Get basic metadata - assignees and priority levels from tracker
        """
        try:
            client = self.create_client()
        except IntegrationException as e:
            self.request.response.status_code = 503
            return {"error_messages": [str(e)]}
        assignees = []
        priorities = []
        issue_types = []
        possible_issue_types = client.get_issue_types(self.request)
        for issue_type in possible_issue_types:
            for field in issue_type["fields"]:
                if field["id"] == "assignee":
                    assignees = field["values"]
                if field["id"] == "priority":
                    priorities = field["values"]
            issue_types.append({"name": issue_type["name"], "id": issue_type["id"]})
        return {
            "assignees": assignees,
            "priorities": priorities,
            "issue_types": issue_types,
        }

    @view_config(
        route_name="integrations_id",
        match_param=["action=create-issue", "integration=jira"],
        renderer="json",
    )
    def create_issue(self):
        """
        Creates a new issue in jira from report group
        """
        report = ReportGroupService.by_id(self.request.unsafe_json_body["group_id"])
        form_data = {
            "title": self.request.unsafe_json_body.get("title", "Unknown Title"),
            "content": self.request.unsafe_json_body.get("content", ""),
            "issue_type": self.request.unsafe_json_body["issue_type"]["id"],
            "priority": self.request.unsafe_json_body["priority"]["id"],
            "responsible": self.request.unsafe_json_body["responsible"]["id"],
            "project": self.integration.config["project"],
        }
        try:
            client = self.create_client()
            issue = client.create_issue(form_data, request=self.request)
        except IntegrationException as e:
            self.request.response.status_code = 503
            return {"error_messages": [str(e)]}

        comment_body = "Jira issue created: %s " % issue["web_url"]
        comment = ReportComment(
            owner_id=self.request.user.id,
            report_time=report.first_timestamp,
            body=comment_body,
        )
        report.comments.append(comment)
        return True

    @view_config(
        route_name="integrations_id",
        match_param=["action=setup", "integration=jira"],
        renderer="json",
        permission="edit",
    )
    def setup(self):
        """
        Validates and creates integration between application and jira
        """
        resource = self.request.context.resource
        form = forms.IntegrationJiraForm(
            MultiDict(self.request.safe_json_body or {}),
            csrf_context=self.request,
            **self.integration_config
        )
        if self.request.method == "POST" and form.validate():
            integration_config = {
                "user_name": form.user_name.data,
                "password": form.password.data,
                "host_name": form.host_name.data,
                "project": form.project.data,
            }
            if not self.integration:
                # add new integration
                self.integration = JiraIntegration(modified_date=datetime.utcnow())
                self.request.session.flash("Integration added")
                resource.integrations.append(self.integration)
            else:
                self.request.session.flash("Integration updated")
            self.integration.config = integration_config
            return integration_config
        elif self.request.method == "POST":
            return HTTPUnprocessableEntity(body=form.errors_json)

        to_return = copy.deepcopy(self.integration_config)
        to_return.pop("password", None)
        return to_return
