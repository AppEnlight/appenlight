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
from appenlight.models.integrations.flowdock import FlowdockIntegration
from webhelpers2.text import truncate

log = logging.getLogger(__name__)


class FlowdockAlertChannel(AlertChannel):
    __mapper_args__ = {"polymorphic_identity": "flowdock"}

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

        app_url = kwargs["request"].registry.settings["_mail_url"]
        destination_url = kwargs["request"].route_url("/", _app_url=app_url)
        f_args = (
            "report",
            template_vars["resource"].resource_id,
            template_vars["url_start_date"].strftime("%Y-%m-%dT%H:%M"),
            template_vars["url_end_date"].strftime("%Y-%m-%dT%H:%M"),
        )
        destination_url += "ui/{}?resource={}&start_date={}&end_date={}".format(*f_args)

        if template_vars["confirmed_total"] > 1:
            template_vars["title"] = "%s - %s reports" % (
                template_vars["resource_name"],
                template_vars["confirmed_total"],
            )
        else:
            error_title = truncate(
                template_vars["reports"][0][1].error or "slow report", 90
            )
            template_vars["title"] = "%s - '%s' report" % (
                template_vars["resource_name"],
                error_title,
            )

        log_msg = "NOTIFY : %s via %s :: %s reports" % (
            kwargs["user"].user_name,
            self.channel_visible_value,
            template_vars["confirmed_total"],
        )
        log.warning(log_msg)

        client = FlowdockIntegration.create_client(self.integration.config["api_token"])
        payload = {
            "source": "AppEnlight",
            "from_address": kwargs["request"].registry.settings["mailing.from_email"],
            "subject": template_vars["title"],
            "content": "New report present",
            "tags": ["appenlight"],
            "link": destination_url,
        }
        client.send_to_inbox(payload)

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

            title = "ALERT %s: %s - %s %s" % (
                template_vars["alert_action"],
                template_vars["resource_name"],
                kwargs["event"].values["reports"],
                template_vars["report_type"],
            )

        else:
            title = "ALERT %s: %s type: %s" % (
                template_vars["alert_action"],
                template_vars["resource_name"],
                template_vars["alert_type"].replace("_", " "),
            )

        client = FlowdockIntegration.create_client(self.integration.config["api_token"])
        payload = {
            "source": "AppEnlight",
            "from_address": kwargs["request"].registry.settings["mailing.from_email"],
            "subject": title,
            "content": "Investigation required",
            "tags": ["appenlight", "alert", template_vars["alert_type"]],
            "link": template_vars["destination_url"],
        }
        client.send_to_inbox(payload)

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

        message = "ALERT %s: %s has uptime issues" % (
            template_vars["alert_action"],
            template_vars["resource_name"],
        )
        submessage = "Info: "
        submessage += template_vars["reason"]

        client = FlowdockIntegration.create_client(self.integration.config["api_token"])
        payload = {
            "source": "AppEnlight",
            "from_address": kwargs["request"].registry.settings["mailing.from_email"],
            "subject": message,
            "content": submessage,
            "tags": ["appenlight", "alert", "uptime"],
            "link": template_vars["destination_url"],
        }
        client.send_to_inbox(payload)

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
        message = "Daily report digest: %s - %s reports" % (
            template_vars["resource_name"],
            template_vars["confirmed_total"],
        )

        f_args = (template_vars["confirmed_total"], template_vars["timestamp"])

        payload = {
            "source": "AppEnlight",
            "from_address": kwargs["request"].registry.settings["mailing.from_email"],
            "subject": message,
            "content": "%s reports in total since %s" % f_args,
            "tags": ["appenlight", "digest"],
            "link": template_vars["destination_url"],
        }

        client = FlowdockIntegration.create_client(self.integration.config["api_token"])
        client.send_to_inbox(payload)

        log_msg = "DIGEST  : %s via %s :: %s reports" % (
            kwargs["user"].user_name,
            self.channel_visible_value,
            template_vars["confirmed_total"],
        )
        log.warning(log_msg)

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

        message = 'ALERT {}: value in "{}" chart ' 'met alert "{}" criteria'.format(
            template_vars["alert_action"],
            template_vars["chart_name"],
            template_vars["action_name"],
        )
        submessage = "Info: "
        for item in template_vars["readable_values"]:
            submessage += "{}: {}\n".format(item["label"], item["value"])

        client = FlowdockIntegration.create_client(self.integration.config["api_token"])
        payload = {
            "source": "AppEnlight",
            "from_address": kwargs["request"].registry.settings["mailing.from_email"],
            "subject": message,
            "content": submessage,
            "tags": ["appenlight", "alert", "chart"],
            "link": template_vars["destination_url"],
        }
        client.send_to_inbox(payload)
