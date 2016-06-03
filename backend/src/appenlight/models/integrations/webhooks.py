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

import logging

import requests

from appenlight.models.integrations import (IntegrationBase,
                                            IntegrationException)
from appenlight.models.alert_channel import AlertChannel
from appenlight.lib.ext_json import json

_ = str

log = logging.getLogger(__name__)


class NotFoundException(Exception):
    pass


class WebhooksIntegration(IntegrationBase):
    __mapper_args__ = {
        'polymorphic_identity': 'webhooks'
    }
    front_visible = False
    as_alert_channel = True
    supports_report_alerting = True
    action_notification = True
    integration_action = 'Message via Webhooks'

    @classmethod
    def create_client(cls, url):
        client = WebhooksClient(url)
        return client


class WebhooksClient(object):
    def __init__(self, url):
        self.api_url = url

    def make_request(self, url, method='get', data=None):
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'appenlight-webhooks',
        }
        try:
            if data:
                data = json.dumps(data)
            resp = getattr(requests, method)(url, data=data, headers=headers,
                                             timeout=3)
        except Exception as e:
            raise IntegrationException(
                _('Error communicating with Webhooks: %s').format(e))
        if resp.status_code > 299:
            raise IntegrationException(
                'Error communicating with Webhooks - status code: %s'.format(
                    resp.status_code))
        return resp

    def send_to_hook(self, payload):
        return self.make_request(self.api_url, method='post',
                                 data=payload).json()


class WebhooksAlertChannel(AlertChannel):
    __mapper_args__ = {
        'polymorphic_identity': 'webhooks'
    }

    def notify_reports(self, **kwargs):
        """
        Notify user of individual reports

        kwargs:
            application: application that the event applies for,
            user: user that should be notified
            request: request object
            since_when: reports are newer than this time value,
            reports: list of reports to render

        """
        template_vars = self.get_notification_basic_vars(kwargs)
        payload = []
        include_keys = ('id', 'http_status', 'report_type', 'resource_name',
                        'front_url', 'resource_id', 'error', 'url_path',
                        'tags', 'duration')

        for occurences, report in kwargs['reports']:
            r_dict = report.last_report_ref.get_dict(kwargs['request'],
                                                     include_keys=include_keys)
            r_dict['group']['occurences'] = occurences
            payload.append(r_dict)
        client = WebhooksIntegration.create_client(
            self.integration.config['reports_webhook'])
        client.send_to_hook(payload)

    def notify_alert(self, **kwargs):
        """
        Notify user of report or uptime threshold events based on events alert type

        Kwargs:
            application: application that the event applies for,
            event: event that is notified,
            user: user that should be notified
            request: request object

        """
        payload = {
            'alert_action': kwargs['event'].unified_alert_action(),
            'alert_name': kwargs['event'].unified_alert_name(),
            'event_time': kwargs['event'].end_date or kwargs[
                'event'].start_date,
            'resource_name': None,
            'resource_id': None
        }
        if kwargs['event'].values and kwargs['event'].values.get('reports'):
            payload['reports'] = kwargs['event'].values.get('reports', [])
        if 'application' in kwargs:
            payload['resource_name'] = kwargs['application'].resource_name
            payload['resource_id'] = kwargs['application'].resource_id

        client = WebhooksIntegration.create_client(
            self.integration.config['alerts_webhook'])
        client.send_to_hook(payload)
