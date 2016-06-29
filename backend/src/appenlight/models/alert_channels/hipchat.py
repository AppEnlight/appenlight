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
from appenlight.models.integrations.hipchat import HipchatIntegration
from webhelpers2.text import truncate

log = logging.getLogger(__name__)


class HipchatAlertChannel(AlertChannel):
    __mapper_args__ = {
        'polymorphic_identity': 'hipchat'
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

        app_url = kwargs['request'].registry.settings['_mail_url']
        destination_url = kwargs['request'].route_url('/',
                                                      _app_url=app_url)
        f_args = ('report',
                  template_vars['resource'].resource_id,
                  template_vars['url_start_date'].strftime('%Y-%m-%dT%H:%M'),
                  template_vars['url_end_date'].strftime('%Y-%m-%dT%H:%M'))
        destination_url += 'ui/{}?resource={}&start_date={}&end_date={}'.format(
            *f_args)

        if template_vars['confirmed_total'] > 1:
            template_vars["title"] = "%s - %s reports" % (
                template_vars['resource_name'],
                template_vars['confirmed_total'],
            )
        else:
            error_title = truncate(template_vars['reports'][0][1].error or
                                   'slow report', 90)
            template_vars["title"] = "%s - '%s' report" % (
                template_vars['resource_name'],
                error_title)

        template_vars["title"] += ' ' + destination_url

        log_msg = 'NOTIFY  : %s via %s :: %s reports' % (
            kwargs['user'].user_name,
            self.channel_visible_value,
            template_vars['confirmed_total'])
        log.warning(log_msg)

        client = HipchatIntegration.create_client(
            self.integration.config['api_token'])
        for room in self.integration.config['rooms'].split(','):
            client.send({
                "message_format": 'text',
                "message": template_vars["title"],
                "from": "AppEnlight",
                "room_id": room.strip(),
                "color": "yellow"
            })

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

            title = 'ALERT %s: %s - %s %s' % (
                template_vars['alert_action'],
                template_vars['resource_name'],
                kwargs['event'].values['reports'],
                template_vars['report_type'],
            )

        else:
            title = 'ALERT %s: %s type: %s' % (
                template_vars['alert_action'],
                template_vars['resource_name'],
                template_vars['alert_type'].replace('_', ' '),
            )

        title += '\n ' + template_vars['destination_url']

        api_token = self.integration.config['api_token']
        client = HipchatIntegration.create_client(api_token)
        for room in self.integration.config['rooms'].split(','):
            client.send({
                "message_format": 'text',
                "message": title,
                "from": "AppEnlight",
                "room_id": room.strip(),
                "color": "red",
                "notify": '1'
            })

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

        message = 'ALERT %s: %s has uptime issues\n' % (
            template_vars['alert_action'],
            template_vars['resource_name'],
        )
        message += template_vars['reason']
        message += '\n{}'.format(template_vars['destination_url'])

        api_token = self.integration.config['api_token']
        client = HipchatIntegration.create_client(api_token)
        for room in self.integration.config['rooms'].split(','):
            client.send({
                "message_format": 'text',
                "message": message,
                "from": "AppEnlight",
                "room_id": room.strip(),
                "color": "red",
                "notify": '1'
            })

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
        message = 'ALERT {}: value in "{}" chart: ' \
                  'met alert "{}" criteria\n'.format(
            template_vars['alert_action'],
            template_vars['chart_name'],
            template_vars['action_name'],
        )

        for item in template_vars['readable_values']:
            message += '{}: {}\n'.format(item['label'], item['value'])

        message += template_vars['destination_url']

        api_token = self.integration.config['api_token']
        client = HipchatIntegration.create_client(api_token)
        for room in self.integration.config['rooms'].split(','):
            client.send({
                "message_format": 'text',
                "message": message,
                "from": "AppEnlight",
                "room_id": room.strip(),
                "color": "red",
                "notify": '1'
            })

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
        f_args = (template_vars['resource_name'],
                  template_vars['confirmed_total'],)
        message = "Daily report digest: %s - %s reports" % f_args
        message += '\n{}'.format(template_vars['destination_url'])
        api_token = self.integration.config['api_token']
        client = HipchatIntegration.create_client(api_token)
        for room in self.integration.config['rooms'].split(','):
            client.send({
                "message_format": 'text',
                "message": message,
                "from": "AppEnlight",
                "room_id": room.strip(),
                "color": "green",
                "notify": '1'
            })

        log_msg = 'DIGEST  : %s via %s :: %s reports' % (
            kwargs['user'].user_name,
            self.channel_visible_value,
            template_vars['confirmed_total'])
        log.warning(log_msg)
