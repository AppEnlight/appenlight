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
import random
from datetime import datetime

from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config

from appenlight.models import DBSession
from appenlight.models.event import Event
from appenlight.models.integrations import IntegrationBase
from appenlight.models.alert_channel import AlertChannel
from appenlight.models.report_group import ReportGroup
from appenlight.models.services.alert_channel import AlertChannelService
from appenlight.lib import generate_random_string

log = logging.getLogger(__name__)

dummy_report = ReportGroup()
dummy_report.error = "ProtocolError: ('Connection aborted.', " \
                     "error(111, 'Connection refused'))"
dummy_report.total_reports = 4
dummy_report.occurences = 4

dummy_report2 = ReportGroup()
dummy_report2.error = "UnboundLocalError: local variable " \
                      "'hits' referenced before assignment"
dummy_report2.total_reports = 8
dummy_report2.occurences = 8

dummy_reports = [(4, dummy_report), (8, dummy_report2)]


class IntegrationView(object):
    """
    Base class for 3rd party integrations setup views
    """

    def __init__(self, request):
        self.request = request
        resource = self.request.context.resource
        integration_name = request.matchdict['integration']
        integration = IntegrationBase.by_app_id_and_integration_name(
            resource.resource_id, integration_name)
        if integration:
            dict_config = integration.config
        else:
            dict_config = {}
        self.integration = integration
        self.integration_config = dict_config

    @view_config(route_name='integrations_id',
                 request_method="DELETE",
                 renderer='json',
                 permission='edit')
    def remove_integration(self):
        if self.integration:
            DBSession.delete(self.integration)
            self.request.session.flash('Integration removed')
        return ''

    @view_config(route_name='integrations_id',
                 request_method="POST",
                 match_param=['action=test_report_notification'],
                 renderer='json',
                 permission='edit')
    def test_report_notification(self):
        if not self.integration:
            self.request.session.flash('Integration needs to be configured',
                                       'warning')
            return False

        resource = self.integration.resource

        channel = AlertChannelService.by_integration_id(self.integration.id)

        if random.random() < 0.5:
            confirmed_reports = dummy_reports
        else:
            confirmed_reports = [random.choice(dummy_reports)]

        channel.notify_reports(resource=resource,
                               user=self.request.user,
                               request=self.request,
                               since_when=datetime.utcnow(),
                               reports=confirmed_reports)
        self.request.session.flash('Report notification sent')
        return True

    @view_config(route_name='integrations_id',
                 request_method="POST",
                 match_param=['action=test_error_alert'],
                 renderer='json',
                 permission='edit')
    def test_error_alert(self):
        if not self.integration:
            self.request.session.flash('Integration needs to be configured',
                                       'warning')
            return False

        resource = self.integration.resource

        event_name = random.choice(('error_report_alert',
                                    'slow_report_alert',))
        new_event = Event(resource_id=resource.resource_id,
                          event_type=Event.types[event_name],
                          start_date=datetime.utcnow(),
                          status=Event.statuses['active'],
                          values={'reports': random.randint(11, 99),
                                  'threshold': 10}
                          )

        channel = AlertChannelService.by_integration_id(self.integration.id)

        channel.notify_alert(resource=resource,
                             event=new_event,
                             user=self.request.user,
                             request=self.request)
        self.request.session.flash('Notification sent')
        return True

    @view_config(route_name='integrations_id',
                 request_method="POST",
                 match_param=['action=test_daily_digest'],
                 renderer='json',
                 permission='edit')
    def test_daily_digest(self):
        if not self.integration:
            self.request.session.flash('Integration needs to be configured',
                                       'warning')
            return False

        resource = self.integration.resource
        channel = AlertChannelService.by_integration_id(self.integration.id)

        channel.send_digest(resource=resource,
                            user=self.request.user,
                            request=self.request,
                            since_when=datetime.utcnow(),
                            reports=dummy_reports)
        self.request.session.flash('Notification sent')
        return True

    @view_config(route_name='integrations_id',
                 request_method="POST",
                 match_param=['action=test_uptime_alert'],
                 renderer='json',
                 permission='edit')
    def test_uptime_alert(self):
        if not self.integration:
            self.request.session.flash('Integration needs to be configured',
                                       'warning')
            return False

        resource = self.integration.resource

        new_event = Event(resource_id=resource.resource_id,
                          event_type=Event.types['uptime_alert'],
                          start_date=datetime.utcnow(),
                          status=Event.statuses['active'],
                          values={"status_code": 500,
                                  "tries": 2,
                                  "response_time": 0})

        channel = AlertChannelService.by_integration_id(self.integration.id)
        channel.notify_uptime_alert(resource=resource,
                                    event=new_event,
                                    user=self.request.user,
                                    request=self.request)

        self.request.session.flash('Notification sent')
        return True

    @view_config(route_name='integrations_id',
                 request_method="POST",
                 match_param=['action=test_chart_alert'],
                 renderer='json',
                 permission='edit')
    def test_chart_alert(self):
        if not self.integration:
            self.request.session.flash('Integration needs to be configured',
                                       'warning')
            return False

        resource = self.integration.resource

        chart_values = {
            "matched_rule": {'name': 'Fraud attempt limit'},
            "matched_step_values": {"labels": {
                "0_1": {"human_label": "Attempts sum"}},
                "values": {"0_1": random.randint(11, 55),
                           "key": "2015-12-16T15:49:00"}},
            "start_interval": datetime.utcnow(),
            "resource": 1,
            "chart_name": "Fraud attempts per day",
            "chart_uuid": "some_uuid",
            "step_size": 3600,
            "action_name": "Notify excessive fraud attempts"}

        new_event = Event(resource_id=resource.resource_id,
                          event_type=Event.types['chart_alert'],
                          status=Event.statuses['active'],
                          values=chart_values,
                          target_uuid="some_uuid",
                          start_date=datetime.utcnow())

        channel = AlertChannelService.by_integration_id(self.integration.id)
        channel.notify_chart_alert(resource=resource,
                                   event=new_event,
                                   user=self.request.user,
                                   request=self.request)

        self.request.session.flash('Notification sent')
        return True

    def create_missing_channel(self, resource, channel_name):
        """
        Recreates alert channel for the owner of integration
        """
        if self.integration:
            if not self.integration.channel:
                channel = AlertChannel()
                channel.channel_name = channel_name
                channel.channel_validated = True
                channel.channel_value = resource.resource_id
                channel.integration_id = self.integration.id
                security_code = generate_random_string(10)
                channel.channel_json_conf = {'security_code': security_code}
                resource.owner.alert_channels.append(channel)
