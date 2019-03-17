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

import json
import requests

from . import IntegrationBase, IntegrationException

_ = str


class GithubAuthException(Exception):
    pass


class GithubIntegration(IntegrationBase):
    __mapper_args__ = {"polymorphic_identity": "github"}
    front_visible = True
    as_alert_channel = False
    supports_report_alerting = False
    action_notification = True
    integration_action = "Add issue to Github"

    @classmethod
    def create_client(cls, request, user_name=None, repo_name=None):
        """
        Creates REST client that can authenticate to specific repo
        uses auth tokens for current request user
        """
        token = None
        secret = None
        for identity in request.user.external_identities:
            if identity.provider_name == "github":
                token = identity.access_token
                secret = identity.token_secret
                break
        if not token:
            raise IntegrationException("No valid auth token present for this service")
        client = GithubClient(token=token, owner=user_name, name=repo_name)
        return client


class GithubClient(object):
    api_url = "https://api.github.com"
    repo_type = "github"

    def __init__(self, token, owner, name):
        self.access_token = token
        self.owner = owner
        self.name = name

    def make_request(self, url, method="get", data=None, headers=None):
        req_headers = {
            "User-Agent": "appenlight",
            "Content-Type": "application/json",
            "Authorization": "token %s" % self.access_token,
        }
        try:
            if data:
                data = json.dumps(data)
            resp = getattr(requests, method)(
                url, data=data, headers=req_headers, timeout=10
            )
        except Exception as e:
            msg = "Error communicating with Github: %s"
            raise IntegrationException(_(msg) % (e,))

        if resp.status_code == 404:
            msg = "User or repo name are incorrect"
            raise IntegrationException(_(msg))
        if resp.status_code == 401:
            msg = "You are not authorized to access this repo"
            raise IntegrationException(_(msg))
        elif resp.status_code not in [200, 201]:
            msg = "Github response_code: %s"
            raise IntegrationException(_(msg) % resp.status_code)
        try:
            return resp.json()
        except Exception as e:
            msg = "Error decoding response from Github: %s"
            raise IntegrationException(_(msg) % (e,))

    def get_statuses(self):
        """Gets list of possible item statuses"""
        url = "%(api_url)s/repos/%(owner)s/%(name)s/labels" % {
            "api_url": self.api_url,
            "owner": self.owner,
            "name": self.name,
        }

        data = self.make_request(url)

        statuses = []
        for status in data:
            statuses.append(status["name"])
        return statuses

    def get_repo(self):
        """Gets list of possible item statuses"""
        url = "%(api_url)s/repos/%(owner)s/%(name)s" % {
            "api_url": self.api_url,
            "owner": self.owner,
            "name": self.name,
        }

        data = self.make_request(url)
        return data

    def get_assignees(self):
        """Gets list of possible assignees"""
        url = "%(api_url)s/repos/%(owner)s/%(name)s/collaborators" % {
            "api_url": self.api_url,
            "owner": self.owner,
            "name": self.name,
        }
        data = self.make_request(url)
        results = []
        for entry in data:
            results.append({"user": entry["login"], "name": entry.get("name")})
        return results

    def create_issue(self, form_data):
        """
        Make a REST call to create issue in Github's issue tracker
        """
        url = "%(api_url)s/repos/%(owner)s/%(name)s/issues" % {
            "api_url": self.api_url,
            "owner": self.owner,
            "name": self.name,
        }

        payload = {
            "title": form_data["title"],
            "body": form_data["content"],
            "labels": [],
            "assignee": form_data["responsible"],
        }
        payload["labels"].extend(form_data["kind"])
        data = self.make_request(url, "post", data=payload)
        to_return = {
            "id": data["number"],
            "resource_url": data["url"],
            "web_url": data["html_url"],
        }
        return to_return
