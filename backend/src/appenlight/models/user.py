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
import sqlalchemy as sa
from datetime import datetime
from appenlight.models import Base, get_db_session
from appenlight.models.services.event import EventService
from appenlight.models.integrations import IntegrationException
from pyramid.threadlocal import get_current_request
from ziggurat_foundations.models.user import UserMixin

log = logging.getLogger(__name__)


class User(UserMixin, Base):
    __possible_permissions__ = []

    first_name = sa.Column(sa.Unicode(25))
    last_name = sa.Column(sa.Unicode(25))
    company_name = sa.Column(sa.Unicode(255), default='')
    company_address = sa.Column(sa.Unicode(255), default='')
    zip_code = sa.Column(sa.Unicode(25), default='')
    city = sa.Column(sa.Unicode(50), default='')
    default_report_sort = sa.Column(sa.Unicode(25), default='newest')
    notes = sa.Column(sa.UnicodeText, default='')
    notifications = sa.Column(sa.Boolean(), default=True)
    registration_ip = sa.Column(sa.UnicodeText(), default='')
    alert_channels = sa.orm.relationship('AlertChannel',
                                         cascade="all,delete-orphan",
                                         passive_deletes=True,
                                         passive_updates=True,
                                         backref='owner',
                                         order_by='AlertChannel.channel_name, '
                                                  'AlertChannel.channel_value')

    alert_actions = sa.orm.relationship('AlertChannelAction',
                                        cascade="all,delete-orphan",
                                        passive_deletes=True,
                                        passive_updates=True,
                                        backref='owner',
                                        order_by='AlertChannelAction.pkey')

    auth_tokens = sa.orm.relationship('AuthToken',
                                      cascade="all,delete-orphan",
                                      passive_deletes=True,
                                      passive_updates=True,
                                      backref='owner',
                                      order_by='AuthToken.creation_date')

    def get_dict(self, exclude_keys=None, include_keys=None,
                 extended_info=False):
        result = super(User, self).get_dict(exclude_keys, include_keys)
        if extended_info:
            result['groups'] = [g.group_name for g in self.groups]
            result['permissions'] = [p.perm_name for p in self.permissions]
            request = get_current_request()
            apps = self.resources_with_perms(
                ['view'], resource_types=['application'])
            result['applications'] = sorted(
                [{'resource_id': a.resource_id,
                  'resource_name': a.resource_name}
                 for a in apps.all()],
                key=lambda x: x['resource_name'].lower())
            result['assigned_reports'] = [r.get_dict(request) for r
                                          in self.assigned_report_groups]
            result['latest_events'] = [ev.get_dict(request) for ev
                                       in self.latest_events()]

        exclude_keys_list = exclude_keys or []
        include_keys_list = include_keys or []
        d = {}
        for k in result.keys():
            if (k not in exclude_keys_list and
                    (k in include_keys_list or not include_keys)):
                d[k] = result[k]
        return d

    def __repr__(self):
        return '<User: %s, id: %s>' % (self.user_name, self.id)

    @property
    def assigned_report_groups(self):
        from appenlight.models.report_group import ReportGroup

        resources = self.resources_with_perms(
            ['view'], resource_types=['application'])
        query = self.assigned_reports_relation
        rid_list = [r.resource_id for r in resources]
        query = query.filter(ReportGroup.resource_id.in_(rid_list))
        query = query.limit(50)
        return query

    def feed_report(self, report):
        """ """
        if not hasattr(self, 'current_reports'):
            self.current_reports = []
        self.current_reports.append(report)

    def send_digest(self, request, application, reports, since_when=None,
                    db_session=None):
        db_session = get_db_session(db_session)
        if not reports:
            return True
        if not since_when:
            since_when = datetime.utcnow()
        for channel in self.alert_channels:
            if not channel.channel_validated or not channel.daily_digest:
                continue
            try:
                channel.send_digest(resource=application,
                                    user=self,
                                    request=request,
                                    since_when=since_when,
                                    reports=reports)
            except IntegrationException as e:
                log.warning('%s' % e)

    def latest_events(self):
        return EventService.latest_for_user(self)
