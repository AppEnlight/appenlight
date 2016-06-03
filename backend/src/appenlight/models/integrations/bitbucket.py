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

import requests
from requests_oauthlib import OAuth1
from appenlight.models.integrations import (IntegrationBase,
                                            IntegrationException)

_ = str


class NotFoundException(Exception):
    pass


class BitbucketIntegration(IntegrationBase):
    __mapper_args__ = {
        'polymorphic_identity': 'bitbucket'
    }
    front_visible = True
    as_alert_channel = False
    supports_report_alerting = False
    action_notification = True
    integration_action = 'Add issue to Bitbucket'

    @classmethod
    def create_client(cls, request, user_name=None, repo_name=None):
        """
        Creates REST client that can authenticate to specific repo
        uses auth tokens for current request user
        """
        config = request.registry.settings
        token = None
        secret = None
        for identity in request.user.external_identities:
            if identity.provider_name == 'bitbucket':
                token = identity.access_token
                secret = identity.token_secret
                break
        if not token:
            raise IntegrationException(
                'No valid auth token present for this service')
        client = BitbucketClient(token, secret,
                                 user_name,
                                 repo_name,
                                 config['authomatic.pr.bitbucket.key'],
                                 config['authomatic.pr.bitbucket.secret'])
        return client


class BitbucketClient(object):
    api_url = 'https://bitbucket.org/api/1.0'
    repo_type = 'bitbucket'

    def __init__(self, token, secret, owner, repo_name, bitbucket_consumer_key,
                 bitbucket_consumer_secret):
        self.access_token = token
        self.token_secret = secret
        self.owner = owner
        self.repo_name = repo_name
        self.bitbucket_consumer_key = bitbucket_consumer_key
        self.bitbucket_consumer_secret = bitbucket_consumer_secret

    possible_keys = {
        'status': ['new', 'open', 'resolved', 'on hold', 'invalid',
                   'duplicate', 'wontfix'],
        'priority': ['trivial', 'minor', 'major', 'critical', 'blocker'],
        'kind': ['bug', 'enhancement', 'proposal', 'task']
    }

    def get_statuses(self):
        """Gets list of possible item statuses"""
        return self.possible_keys['status']

    def get_priorities(self):
        """Gets list of possible item statuses"""
        return self.possible_keys['priority']

    def make_request(self, url, method='get', data=None, headers=None):
        """
        Performs HTTP request to bitbucket
        """
        auth = OAuth1(self.bitbucket_consumer_key,
                      self.bitbucket_consumer_secret,
                      self.access_token, self.token_secret)
        try:
            resp = getattr(requests, method)(url, data=data, auth=auth,
                                             timeout=10)
        except Exception as e:
            raise IntegrationException(
                _('Error communicating with Bitbucket: %s') % (e,))
        if resp.status_code == 401:
            raise IntegrationException(
                _('You are not authorized to access this repo'))
        elif resp.status_code == 404:
            raise IntegrationException(_('User or repo name are incorrect'))
        elif resp.status_code not in [200, 201]:
            raise IntegrationException(
                _('Bitbucket response_code: %s') % resp.status_code)
        try:
            return resp.json()
        except Exception as e:
            raise IntegrationException(
                _('Error decoding response from Bitbucket: %s') % (e,))

    def get_assignees(self):
        """Gets list of possible assignees"""
        url = '%(api_url)s/privileges/%(owner)s/%(repo_name)s' % {
            'api_url': self.api_url,
            'owner': self.owner,
            'repo_name': self.repo_name}

        data = self.make_request(url)
        results = [{'user': self.owner, 'name': '(Repo owner)'}]
        if data:
            for entry in data:
                results.append({"user": entry['user']['username'],
                                "name": entry['user'].get('display_name')})
        return results

    def create_issue(self, form_data):
        """
        Sends creates a new issue in tracker using REST call
        """
        url = '%(api_url)s/repositories/%(owner)s/%(repo_name)s/issues/' % {
            'api_url': self.api_url,
            'owner': self.owner,
            'repo_name': self.repo_name}

        payload = {
            "title": form_data['title'],
            "content": form_data['content'],
            "kind": form_data['kind'],
            "priority": form_data['priority'],
            "responsible": form_data['responsible']
        }
        data = self.make_request(url, 'post', payload)
        f_args = {
            "owner": self.owner,
            "repo_name": self.repo_name,
            "issue_id": data['local_id']
        }
        web_url = 'https://bitbucket.org/%(owner)s/%(repo_name)s' \
                  '/issue/%(issue_id)s/issue-title' % f_args
        to_return = {
            'id': data['local_id'],
            'resource_url': data['resource_uri'],
            'web_url': web_url
        }
        return to_return
