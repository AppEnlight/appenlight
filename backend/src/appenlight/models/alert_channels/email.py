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
from appenlight.models.services.user import UserService
from webhelpers2.text import truncate

log = logging.getLogger(__name__)


class EmailAlertChannel(AlertChannel):
    """
    Default email alerting channel
    """

    __mapper_args__ = {"polymorphic_identity": "email"}

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

        if template_vars["confirmed_total"] > 1:
            template_vars["title"] = "AppEnlight :: %s - %s reports" % (
                template_vars["resource_name"],
                template_vars["confirmed_total"],
            )
        else:
            error_title = truncate(
                template_vars["reports"][0][1].error or "slow report", 20
            )
            template_vars["title"] = "AppEnlight :: %s - '%s' report" % (
                template_vars["resource_name"],
                error_title,
            )
        UserService.send_email(
            kwargs["request"],
            [self.channel_value],
            template_vars,
            "/email_templates/notify_reports.jinja2",
        )
        log_msg = "NOTIFY  : %s via %s :: %s reports" % (
            kwargs["user"].user_name,
            self.channel_visible_value,
            template_vars["confirmed_total"],
        )
        log.warning(log_msg)

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
        title = "AppEnlight :: Daily report digest: %s - %s reports"
        template_vars["email_title"] = title % (
            template_vars["resource_name"],
            template_vars["confirmed_total"],
        )

        UserService.send_email(
            kwargs["request"],
            [self.channel_value],
            template_vars,
            "/email_templates/notify_reports.jinja2",
            immediately=True,
            silent=True,
        )
        log_msg = "DIGEST  : %s via %s :: %s reports" % (
            kwargs["user"].user_name,
            self.channel_visible_value,
            template_vars["confirmed_total"],
        )
        log.warning(log_msg)

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

        if kwargs["event"].unified_alert_action() == "OPEN":
            title = "AppEnlight :: ALERT %s: %s - %s %s" % (
                template_vars["alert_action"],
                template_vars["resource_name"],
                kwargs["event"].values["reports"],
                template_vars["report_type"],
            )
        else:
            title = "AppEnlight :: ALERT %s: %s type: %s" % (
                template_vars["alert_action"],
                template_vars["resource_name"],
                template_vars["alert_type"].replace("_", " "),
            )
        template_vars["email_title"] = title
        UserService.send_email(
            kwargs["request"],
            [self.channel_value],
            template_vars,
            "/email_templates/alert_reports.jinja2",
        )

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
        title = "AppEnlight :: ALERT %s: %s has uptime issues" % (
            template_vars["alert_action"],
            template_vars["resource_name"],
        )
        template_vars["email_title"] = title

        UserService.send_email(
            kwargs["request"],
            [self.channel_value],
            template_vars,
            "/email_templates/alert_uptime.jinja2",
        )

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

        title = (
            'AppEnlight :: ALERT {} value in "{}" chart'
            ' met alert "{}" criteria'.format(
                template_vars["alert_action"],
                template_vars["chart_name"],
                template_vars["action_name"],
            )
        )
        template_vars["email_title"] = title
        UserService.send_email(
            kwargs["request"],
            [self.channel_value],
            template_vars,
            "/email_templates/alert_chart.jinja2",
        )
