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
from appenlight.models.alert_channel import AlertChannel
from appenlight.models.integrations.slack import SlackIntegration
from webhelpers2.text import truncate

log = logging.getLogger(__name__)


class SlackAlertChannel(AlertChannel):
    __mapper_args__ = {
        'polymorphic_identity': 'slack'
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
        template_vars = self.report_alert_notification_vars(kwargs)
        template_vars["title"] = template_vars['resource_name']

        if template_vars['confirmed_total'] > 1:
            template_vars['subtext'] = '%s reports' % template_vars[
                'confirmed_total']
        else:
            error_title = truncate(template_vars['reports'][0][1].error or
                                   'slow report', 90)
            template_vars['subtext'] = error_title

        log_msg = 'NOTIFY  : %s via %s :: %s reports' % (
            kwargs['user'].user_name,
            self.channel_visible_value,
            template_vars['confirmed_total'])
        log.warning(log_msg)

        client = SlackIntegration.create_client(
            self.integration.config['webhook_url'])
        report_data = {
            "username": "AppEnlight",
            "icon_emoji": ":fire:",
            "attachments": [
                {
                    "mrkdwn_in": ["text", "pretext", "title", "fallback"],
                    "fallback": "*%s* - <%s| Browse>" % (
                        template_vars["title"],
                        template_vars['destination_url']),
                    "pretext": "*%s* - <%s| Browse>" % (
                        template_vars["title"],
                        template_vars['destination_url']),
                    "color": "warning",
                    "fields": [
                        {
                            "value": 'Info: %s' % template_vars['subtext'],
                            "short": False
                        }
                    ]
                }
            ]
        }
        client.make_request(data=report_data)

    def notify_report_alert(self, **kwargs):
        """
        Build and send report alert notification

        Kwargs:
            application: application that the event applies for,
            event: event that is notified,
            user: user that should be notified
            request: request object

        """
        template_vars = self.report_alert_notification_vars(kwargs)

        if kwargs['event'].unified_alert_action() == 'OPEN':
            title = '*ALERT %s*: %s' % (
                template_vars['alert_action'],
                template_vars['resource_name']
            )

            template_vars['subtext'] = 'Got at least %s %s' % (
                kwargs['event'].values['reports'],
                template_vars['report_type']
            )

        else:
            title = '*ALERT %s*: %s' % (
                template_vars['alert_action'],
                template_vars['resource_name'],
            )

            template_vars['subtext'] = ''

        alert_type = template_vars['alert_type'].replace('_', ' ')
        alert_type = alert_type.replace('alert', '').capitalize()

        template_vars['type'] = "Type: %s" % alert_type

        client = SlackIntegration.create_client(
            self.integration.config['webhook_url']
        )
        report_data = {
            "username": "AppEnlight",
            "icon_emoji": ":rage:",
            "attachments": [
                {
                    "mrkdwn_in": ["text", "pretext", "title", "fallback"],
                    "fallback": "%s - <%s| Browse>" % (
                        title, template_vars['destination_url']),
                    "pretext": "%s - <%s| Browse>" % (
                        title, template_vars['destination_url']),
                    "color": "danger",
                    "fields": [
                        {
                            "title": template_vars['type'],
                            "value": template_vars['subtext'],
                            "short": False
                        }
                    ]
                }
            ]
        }
        client.make_request(data=report_data)

    def notify_uptime_alert(self, **kwargs):
        """
        Build and send uptime alert notification

        Kwargs:
            application: application that the event applies for,
            event: event that is notified,
            user: user that should be notified
            request: request object

        """
        template_vars = self.uptime_alert_notification_vars(kwargs)

        title = '*ALERT %s*: %s' % (
            template_vars['alert_action'],
            template_vars['resource_name'],
        )
        client = SlackIntegration.create_client(
            self.integration.config['webhook_url']
        )
        report_data = {
            "username": "AppEnlight",
            "icon_emoji": ":rage:",
            "attachments": [
                {
                    "mrkdwn_in": ["text", "pretext", "title", "fallback"],
                    "fallback": "{} - <{}| Browse>".format(
                        title, template_vars['destination_url']),
                    "pretext": "{} - <{}| Browse>".format(
                        title, template_vars['destination_url']),
                    "color": "danger",
                    "fields": [
                        {
                            "title": "Application has uptime issues",
                            "value": template_vars['reason'],
                            "short": False
                        }
                    ]
                }
            ]
        }
        client.make_request(data=report_data)

    def notify_chart_alert(self, **kwargs):
        """
        Build and send chart alert notification

        Kwargs:
            application: application that the event applies for,
            event: event that is notified,
            user: user that should be notified
            request: request object

        """
        template_vars = self.chart_alert_notification_vars(kwargs)

        title = '*ALERT {}*: value in *"{}"* chart ' \
                'met alert *"{}"* criteria'.format(
            template_vars['alert_action'],
            template_vars['chart_name'],
            template_vars['action_name'],
        )

        subtext = ''
        for item in template_vars['readable_values']:
            subtext += '{} - {}\n'.format(item['label'], item['value'])

        client = SlackIntegration.create_client(
            self.integration.config['webhook_url']
        )
        report_data = {
            "username": "AppEnlight",
            "icon_emoji": ":rage:",
            "attachments": [
                {"mrkdwn_in": ["text", "pretext", "title", "fallback"],
                 "fallback": "{} - <{}| Browse>".format(
                     title, template_vars['destination_url']),
                 "pretext": "{} - <{}| Browse>".format(
                     title, template_vars['destination_url']),
                 "color": "danger",
                 "fields": [
                     {
                         "title": "Following criteria were met:",
                         "value": subtext,
                         "short": False
                     }
                 ]
                 }
            ]
        }
        client.make_request(data=report_data)

    def send_digest(self, **kwargs):
        """
        Build and send daily digest notification

        kwargs:
            application: application that the event applies for,
            user: user that should be notified
            request: request object
            since_when: reports are newer than this time value,
            reports: list of reports to render

        """
        template_vars = self.report_alert_notification_vars(kwargs)
        title = "*Daily report digest*: %s" % template_vars['resource_name']

        subtext = '%s reports' % template_vars['confirmed_total']

        client = SlackIntegration.create_client(
            self.integration.config['webhook_url']
        )
        report_data = {
            "username": "AppEnlight",
            "attachments": [
                {
                    "mrkdwn_in": ["text", "pretext", "title", "fallback"],
                    "fallback": "%s : <%s| Browse>" % (
                        title, template_vars['destination_url']),
                    "pretext": "%s: <%s| Browse>" % (
                        title, template_vars['destination_url']),
                    "color": "good",
                    "fields": [
                        {
                            "title": "Got at least: %s" % subtext,
                            "short": False
                        }
                    ]
                }
            ]
        }
        client.make_request(data=report_data)

        log_msg = 'DIGEST  : %s via %s :: %s reports' % (
            kwargs['user'].user_name,
            self.channel_visible_value,
            template_vars['confirmed_total'])
        log.warning(log_msg)
