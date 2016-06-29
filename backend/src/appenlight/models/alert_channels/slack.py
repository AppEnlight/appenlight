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
