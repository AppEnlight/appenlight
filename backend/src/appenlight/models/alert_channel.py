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
import sqlalchemy as sa
import urllib.request, urllib.parse, urllib.error
from datetime import timedelta
from appenlight.models import Base
from appenlight.lib.utils.date_utils import convert_date
from sqlalchemy.dialects.postgresql import JSON
from ziggurat_foundations.models.base import BaseModel

log = logging.getLogger(__name__)

#
channel_rules_m2m_table = sa.Table(
    'channels_actions', Base.metadata,
    sa.Column('channel_pkey', sa.Integer,
              sa.ForeignKey('alert_channels.pkey')),
    sa.Column('action_pkey', sa.Integer,
              sa.ForeignKey('alert_channels_actions.pkey'))
)

DATE_FRMT = '%Y-%m-%dT%H:%M'


class AlertChannel(Base, BaseModel):
    """
    Stores information about possible alerting options
    """
    __tablename__ = 'alert_channels'
    __possible_channel_names__ = ['email']
    __mapper_args__ = {
        'polymorphic_on': 'channel_name',
        'polymorphic_identity': 'integration'
    }

    owner_id = sa.Column(sa.Unicode(30),
                         sa.ForeignKey('users.id', onupdate='CASCADE',
                                       ondelete='CASCADE'))
    channel_name = sa.Column(sa.Unicode(25), nullable=False)
    channel_value = sa.Column(sa.Unicode(80), nullable=False, default='')
    channel_json_conf = sa.Column(JSON(), nullable=False, default='')
    channel_validated = sa.Column(sa.Boolean, nullable=False,
                                  default=False)
    send_alerts = sa.Column(sa.Boolean, nullable=False,
                            default=True)
    daily_digest = sa.Column(sa.Boolean, nullable=False,
                             default=True)
    integration_id = sa.Column(sa.Integer, sa.ForeignKey('integrations.id'),
                               nullable=True)
    pkey = sa.Column(sa.Integer(), nullable=False, primary_key=True)

    channel_actions = sa.orm.relationship('AlertChannelAction',
                                          cascade="all",
                                          passive_deletes=True,
                                          passive_updates=True,
                                          secondary=channel_rules_m2m_table,
                                          backref='channels')

    @property
    def channel_visible_value(self):
        if self.integration:
            return '{}: {}'.format(
                self.channel_name,
                self.integration.resource.resource_name
            )

        return '{}: {}'.format(
            self.channel_name,
            self.channel_value
        )

    def get_dict(self, exclude_keys=None, include_keys=None,
                 extended_info=True):
        """
        Returns dictionary with required information that will be consumed by
        angular
        """
        instance_dict = super(AlertChannel, self).get_dict(exclude_keys,
                                                           include_keys)
        exclude_keys_list = exclude_keys or []
        include_keys_list = include_keys or []

        instance_dict['supports_report_alerting'] = True
        instance_dict['channel_visible_value'] = self.channel_visible_value

        if extended_info:
            instance_dict['actions'] = [
                rule.get_dict(extended_info=True) for
                rule in self.channel_actions]

        del instance_dict['channel_json_conf']

        if self.integration:
            instance_dict[
                'supports_report_alerting'] = \
                self.integration.supports_report_alerting
        d = {}
        for k in instance_dict.keys():
            if (k not in exclude_keys_list and
                    (k in include_keys_list or not include_keys)):
                d[k] = instance_dict[k]
        return d

    def __repr__(self):
        return '<AlertChannel: (%s,%s), user:%s>' % (self.channel_name,
                                                     self.channel_value,
                                                     self.user_name,)

    def send_digest(self, **kwargs):
        """
        This should implement daily top error report notifications
        """
        log.warning('send_digest NOT IMPLEMENTED')

    def notify_reports(self, **kwargs):
        """
        This should implement notification of reports that occured in 1 min
        interval
        """
        log.warning('notify_reports NOT IMPLEMENTED')

    def notify_alert(self, **kwargs):
        """
        Notify user of report/uptime/chart threshold events based on events alert
        type

        Kwargs:
            application: application that the event applies for,
            event: event that is notified,
            user: user that should be notified
            request: request object

        """
        alert_name = kwargs['event'].unified_alert_name()
        if alert_name in ['slow_report_alert', 'error_report_alert']:
            self.notify_report_alert(**kwargs)
        elif alert_name == 'uptime_alert':
            self.notify_uptime_alert(**kwargs)
        elif alert_name == 'chart_alert':
            self.notify_chart_alert(**kwargs)

    def notify_chart_alert(self, **kwargs):
        """
        This should implement report open/close alerts notifications
        """
        log.warning('notify_chart_alert NOT IMPLEMENTED')

    def notify_report_alert(self, **kwargs):
        """
        This should implement report open/close alerts notifications
        """
        log.warning('notify_report_alert NOT IMPLEMENTED')

    def notify_uptime_alert(self, **kwargs):
        """
        This should implement uptime open/close alerts notifications
        """
        log.warning('notify_uptime_alert NOT IMPLEMENTED')

    def get_notification_basic_vars(self, kwargs):
        """
        Sets most common variables used later for rendering notifications for
        channel
        """
        if 'event' in kwargs:
            kwargs['since_when'] = kwargs['event'].start_date

        url_start_date = kwargs.get('since_when') - timedelta(minutes=1)
        url_end_date = kwargs.get('since_when') + timedelta(minutes=4)
        tmpl_vars = {
            "timestamp": kwargs['since_when'],
            "user": kwargs['user'],
            "since_when": kwargs.get('since_when'),
            "url_start_date": url_start_date,
            "url_end_date": url_end_date
        }
        tmpl_vars["resource_name"] = kwargs['resource'].resource_name
        tmpl_vars["resource"] = kwargs['resource']

        if 'event' in kwargs:
            tmpl_vars['event_values'] = kwargs['event'].values
            tmpl_vars['alert_type'] = kwargs['event'].unified_alert_name()
            tmpl_vars['alert_action'] = kwargs['event'].unified_alert_action()
        return tmpl_vars

    def report_alert_notification_vars(self, kwargs):
        tmpl_vars = self.get_notification_basic_vars(kwargs)
        reports = kwargs.get('reports', [])
        tmpl_vars["reports"] = reports
        tmpl_vars["confirmed_total"] = len(reports)

        tmpl_vars["report_type"] = "error reports"
        tmpl_vars["url_report_type"] = 'report/list'

        alert_type = tmpl_vars.get('alert_type', '')
        if 'slow_report' in alert_type:
            tmpl_vars["report_type"] = "slow reports"
            tmpl_vars["url_report_type"] = 'report/list_slow'

        app_url = kwargs['request'].registry.settings['_mail_url']

        destination_url = kwargs['request'].route_url('/',
                                                      _app_url=app_url)
        if alert_type:
            destination_url += 'ui/{}?resource={}&start_date={}&end_date={}'.format(
                tmpl_vars["url_report_type"],
                tmpl_vars['resource'].resource_id,
                tmpl_vars['url_start_date'].strftime(DATE_FRMT),
                tmpl_vars['url_end_date'].strftime(DATE_FRMT)
            )
        else:
            destination_url += 'ui/{}?resource={}'.format(
                tmpl_vars["url_report_type"],
                tmpl_vars['resource'].resource_id
            )
        tmpl_vars["destination_url"] = destination_url

        return tmpl_vars

    def uptime_alert_notification_vars(self, kwargs):
        tmpl_vars = self.get_notification_basic_vars(kwargs)
        app_url = kwargs['request'].registry.settings['_mail_url']
        destination_url = kwargs['request'].route_url('/', _app_url=app_url)
        destination_url += 'ui/{}?resource={}'.format(
            'uptime',
            tmpl_vars['resource'].resource_id)
        tmpl_vars['destination_url'] = destination_url

        reason = ''
        e_values = tmpl_vars.get('event_values')

        if e_values and e_values.get('response_time') == 0:
            reason += ' Response time was slower than 20 seconds.'
        elif e_values:
            code = e_values.get('status_code')
            reason += ' Response status code: %s.' % code

        tmpl_vars['reason'] = reason
        return tmpl_vars

    def chart_alert_notification_vars(self, kwargs):
        tmpl_vars = self.get_notification_basic_vars(kwargs)
        tmpl_vars['chart_name'] = tmpl_vars['event_values']['chart_name']
        tmpl_vars['action_name'] = tmpl_vars['event_values'].get(
            'action_name') or ''
        matched_values = tmpl_vars['event_values']['matched_step_values']
        tmpl_vars['readable_values'] = []
        for key, value in list(matched_values['values'].items()):
            matched_label = matched_values['labels'].get(key)
            if matched_label:
                tmpl_vars['readable_values'].append({
                    'label': matched_label['human_label'],
                    'value': value
                })
        tmpl_vars['readable_values'] = sorted(tmpl_vars['readable_values'],
                                              key=lambda x: x['label'])
        start_date = convert_date(tmpl_vars['event_values']['start_interval'])
        end_date = None
        if tmpl_vars['event_values'].get('end_interval'):
            end_date = convert_date(tmpl_vars['event_values']['end_interval'])

        app_url = kwargs['request'].registry.settings['_mail_url']
        destination_url = kwargs['request'].route_url('/', _app_url=app_url)
        to_encode = {
            'resource': tmpl_vars['event_values']['resource'],
            'start_date': start_date.strftime(DATE_FRMT),
        }
        if end_date:
            to_encode['end_date'] = end_date.strftime(DATE_FRMT)

        destination_url += 'ui/{}?{}'.format(
            'logs',
            urllib.parse.urlencode(to_encode)
        )
        tmpl_vars['destination_url'] = destination_url
        return tmpl_vars
