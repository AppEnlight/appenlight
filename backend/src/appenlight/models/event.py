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

import sqlalchemy as sa
import logging

from datetime import datetime
from appenlight.models import Base, get_db_session
from appenlight.models.services.report_stat import ReportStatService
from appenlight.models.resource import Resource
from appenlight.models.integrations import IntegrationException
from pyramid.threadlocal import get_current_request
from sqlalchemy.dialects.postgresql import JSON
from ziggurat_foundations.models.base import BaseModel

log = logging.getLogger(__name__)


class Event(Base, BaseModel):
    __tablename__ = 'events'

    types = {'error_report_alert': 1,
             'slow_report_alert': 3,
             'comment': 5,
             'assignment': 6,
             'uptime_alert': 7,
             'chart_alert': 9}

    statuses = {'active': 1,
                'closed': 0}

    id = sa.Column(sa.Integer, primary_key=True)
    start_date = sa.Column(sa.DateTime, default=datetime.utcnow)
    end_date = sa.Column(sa.DateTime)
    status = sa.Column(sa.Integer, default=1)
    event_type = sa.Column(sa.Integer, default=1)
    origin_user_id = sa.Column(sa.Integer(), sa.ForeignKey('users.id'),
                               nullable=True)
    target_user_id = sa.Column(sa.Integer(), sa.ForeignKey('users.id'),
                               nullable=True)
    resource_id = sa.Column(sa.Integer(),
                            sa.ForeignKey('resources.resource_id'),
                            nullable=True)
    target_id = sa.Column(sa.Integer)
    target_uuid = sa.Column(sa.Unicode(40))
    text = sa.Column(sa.UnicodeText())
    values = sa.Column(JSON(), nullable=False, default=None)

    def __repr__(self):
        return '<Event %s, app:%s, %s>' % (self.unified_alert_name(),
                                            self.resource_id,
                                            self.unified_alert_action())

    @property
    def reverse_types(self):
        return dict([(v, k) for k, v in self.types.items()])

    def unified_alert_name(self):
        return self.reverse_types[self.event_type]

    def unified_alert_action(self):
        event_name = self.reverse_types[self.event_type]
        if self.status == Event.statuses['closed']:
            return "CLOSE"
        if self.status != Event.statuses['closed']:
            return "OPEN"
        return event_name

    def send_alerts(self, request=None, resource=None, db_session=None):
        """" Sends alerts to applicable channels """
        db_session = get_db_session(db_session)
        db_session.flush()
        if not resource:
            resource = Resource.by_resource_id(self.resource_id)
        if not request:
            request = get_current_request()
        if not resource:
            return
        users = set([p.user for p in resource.users_for_perm('view')])
        for user in users:
            for channel in user.alert_channels:
                if not channel.channel_validated or not channel.send_alerts:
                    continue
                else:
                    try:
                        channel.notify_alert(resource=resource,
                                             event=self,
                                             user=user,
                                             request=request)
                    except IntegrationException as e:
                        log.warning('%s' % e)

    def validate_or_close(self, since_when, db_session=None):
        """ Checks if alerts should stay open or it's time to close them.
            Generates close alert event if alerts get closed """
        event_types = [Event.types['error_report_alert'],
                       Event.types['slow_report_alert']]
        app = Resource.by_resource_id(self.resource_id)
        if self.event_type in event_types:
            total = ReportStatService.count_by_type(
                self.event_type, self.resource_id, since_when)
            if Event.types['error_report_alert'] == self.event_type:
                threshold = app.error_report_threshold
            if Event.types['slow_report_alert'] == self.event_type:
                threshold = app.slow_report_threshold

            if total < threshold:
                self.close()

    def close(self, db_session=None):
        """
        Closes an event and sends notification to affected users
        """
        self.end_date = datetime.utcnow()
        self.status = Event.statuses['closed']
        log.warning('ALERT: CLOSE: %s' % self)
        self.send_alerts()

    def text_representation(self):
        alert_type = self.unified_alert_name()
        text = ''
        if 'slow_report' in alert_type:
            text += 'Slow report alert'
        if 'error_report' in alert_type:
            text += 'Exception report alert'
        if 'uptime_alert' in alert_type:
            text += 'Uptime alert'
        if 'chart_alert' in alert_type:
            text += 'Metrics value alert'

        alert_action = self.unified_alert_action()
        if alert_action == 'OPEN':
            text += ' got opened.'
        if alert_action == 'CLOSE':
            text += ' got closed.'
        return text

    def get_dict(self, request=None):
        dict_data = super(Event, self).get_dict()
        dict_data['text'] = self.text_representation()
        dict_data['resource_name'] = self.resource.resource_name
        return dict_data
