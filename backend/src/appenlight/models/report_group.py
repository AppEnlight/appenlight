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

from pyramid.threadlocal import get_current_request
from sqlalchemy.dialects.postgresql import JSON
from ziggurat_foundations.models.base import BaseModel

from appenlight.models import Base, get_db_session, Datastores
from appenlight.lib.enums import ReportType
from appenlight.lib.rule import Rule
from appenlight.lib.redis_keys import REDIS_KEYS
from appenlight.models.report import REPORT_TYPE_MATRIX

log = logging.getLogger(__name__)


class ReportGroup(Base, BaseModel):
    __tablename__ = 'reports_groups'
    __table_args__ = {'implicit_returning': False}

    id = sa.Column(sa.BigInteger(), nullable=False, primary_key=True)
    resource_id = sa.Column(sa.Integer(),
                            sa.ForeignKey('applications.resource_id',
                                          onupdate='CASCADE',
                                          ondelete='CASCADE'),
                            nullable=False,
                            index=True)
    priority = sa.Column(sa.Integer, nullable=False, index=True, default=5,
                         server_default='5')
    first_timestamp = sa.Column(sa.DateTime(), default=datetime.utcnow,
                                server_default=sa.func.now())
    last_timestamp = sa.Column(sa.DateTime(), default=datetime.utcnow,
                               server_default=sa.func.now())
    error = sa.Column(sa.UnicodeText(), index=True)
    grouping_hash = sa.Column(sa.String(40), default='')
    triggered_postprocesses_ids = sa.Column(JSON(), nullable=False,
                                            default=list)
    report_type = sa.Column(sa.Integer, default=1)
    total_reports = sa.Column(sa.Integer, default=1)
    last_report = sa.Column(sa.Integer)
    occurences = sa.Column(sa.Integer, default=1)
    average_duration = sa.Column(sa.Float, default=0)
    summed_duration = sa.Column(sa.Float, default=0)
    read = sa.Column(sa.Boolean(), index=True, default=False)
    fixed = sa.Column(sa.Boolean(), index=True, default=False)
    notified = sa.Column(sa.Boolean(), index=True, default=False)
    public = sa.Column(sa.Boolean(), index=True, default=False)

    reports = sa.orm.relationship('Report',
                                  lazy='dynamic',
                                  backref='report_group',
                                  cascade="all, delete-orphan",
                                  passive_deletes=True,
                                  passive_updates=True, )

    comments = sa.orm.relationship('ReportComment',
                                   lazy='dynamic',
                                   backref='report',
                                   cascade="all, delete-orphan",
                                   passive_deletes=True,
                                   passive_updates=True,
                                   order_by="ReportComment.comment_id")

    assigned_users = sa.orm.relationship('User',
                                         backref=sa.orm.backref(
                                             'assigned_reports_relation',
                                             lazy='dynamic',
                                             order_by=sa.desc(
                                                 "reports_groups.id")
                                         ),
                                         passive_deletes=True,
                                         passive_updates=True,
                                         secondary='reports_assignments',
                                         order_by="User.user_name")

    stats = sa.orm.relationship('ReportStat',
                                lazy='dynamic',
                                backref='report',
                                passive_deletes=True,
                                passive_updates=True, )

    last_report_ref = sa.orm.relationship('Report',
                                          uselist=False,
                                          primaryjoin="ReportGroup.last_report "
                                                      "== Report.id",
                                          foreign_keys="Report.id",
                                          cascade="all, delete-orphan",
                                          passive_deletes=True,
                                          passive_updates=True, )

    def __repr__(self):
        return '<ReportGroup id:{}>'.format(self.id)

    def get_report(self, report_id=None, public=False):
        """
        Gets report with specific id or latest report if id was not specified
        """
        from .report import Report

        if not report_id:
            return self.last_report_ref
        else:
            return self.reports.filter(Report.id == report_id).first()

    def get_public_url(self, request, _app_url=None):
        url = request.route_url('/', _app_url=_app_url)
        return (url + 'ui/report/%s') % self.id

    def run_postprocessing(self, report):
        """
        Alters report group priority based on postprocessing configuration
        """
        request = get_current_request()
        get_db_session(None, self).flush()
        for action in self.application.postprocess_conf:
            get_db_session(None, self).flush()
            rule_obj = Rule(action.rule, REPORT_TYPE_MATRIX)
            report_dict = report.get_dict(request)
            # if was not processed yet
            if (rule_obj.match(report_dict) and
                        action.pkey not in self.triggered_postprocesses_ids):
                action.postprocess(self)
                # this way sqla can track mutation of list
                self.triggered_postprocesses_ids = \
                    self.triggered_postprocesses_ids + [action.pkey]

        get_db_session(None, self).flush()
        # do not go out of bounds
        if self.priority < 1:
            self.priority = 1
        if self.priority > 10:
            self.priority = 10

    def get_dict(self, request):
        instance_dict = super(ReportGroup, self).get_dict()
        instance_dict['server_name'] = self.get_report().tags.get(
            'server_name')
        instance_dict['view_name'] = self.get_report().tags.get('view_name')
        instance_dict['resource_name'] = self.application.resource_name
        instance_dict['report_type'] = self.get_report().report_type
        instance_dict['url_path'] = self.get_report().url_path
        instance_dict['front_url'] = self.get_report().get_public_url(request)
        del instance_dict['triggered_postprocesses_ids']
        return instance_dict

    def es_doc(self):
        return {
            '_id': str(self.id),
            'pg_id': str(self.id),
            'resource_id': self.resource_id,
            'error': self.error,
            'fixed': self.fixed,
            'public': self.public,
            'read': self.read,
            'priority': self.priority,
            'occurences': self.occurences,
            'average_duration': self.average_duration,
            'summed_duration': self.summed_duration,
            'first_timestamp': self.first_timestamp,
            'last_timestamp': self.last_timestamp
        }

    def set_notification_info(self, notify_10=False, notify_100=False):
        """
        Update redis notification maps for notification job
        """
        current_time = datetime.utcnow().replace(second=0, microsecond=0)
        # global app counter
        key = REDIS_KEYS['counters']['reports_per_type'].format(
            self.report_type, current_time)
        redis_pipeline = Datastores.redis.pipeline()
        redis_pipeline.incr(key)
        redis_pipeline.expire(key, 3600 * 24)
        # detailed app notification for alerts and notifications
        redis_pipeline.sadd(
            REDIS_KEYS['apps_that_had_reports'], self.resource_id)
        redis_pipeline.sadd(
            REDIS_KEYS['apps_that_had_reports_alerting'], self.resource_id)
        # only notify for exceptions here
        if self.report_type == ReportType.error:
            redis_pipeline.sadd(
                REDIS_KEYS['apps_that_had_reports'], self.resource_id)
            redis_pipeline.sadd(
                REDIS_KEYS['apps_that_had_error_reports_alerting'],
                self.resource_id)
        key = REDIS_KEYS['counters']['report_group_occurences'].format(self.id)
        redis_pipeline.incr(key)
        redis_pipeline.expire(key, 3600 * 24)
        key = REDIS_KEYS['counters']['report_group_occurences_alerting'].format(self.id)
        redis_pipeline.incr(key)
        redis_pipeline.expire(key, 3600 * 24)

        if notify_10:
            key = REDIS_KEYS['counters'][
                'report_group_occurences_10th'].format(self.id)
            redis_pipeline.setex(key, 3600 * 24, 1)
        if notify_100:
            key = REDIS_KEYS['counters'][
                'report_group_occurences_100th'].format(self.id)
            redis_pipeline.setex(key, 3600 * 24, 1)

        key = REDIS_KEYS['reports_to_notify_per_type_per_app'].format(
            self.report_type, self.resource_id)
        redis_pipeline.sadd(key, self.id)
        redis_pipeline.expire(key, 3600 * 24)
        key = REDIS_KEYS['reports_to_notify_per_type_per_app_alerting'].format(
            self.report_type, self.resource_id)
        redis_pipeline.sadd(key, self.id)
        redis_pipeline.expire(key, 3600 * 24)
        redis_pipeline.execute()

    @property
    def partition_id(self):
        return 'rcae_r_%s' % self.first_timestamp.strftime('%Y_%m')


def after_insert(mapper, connection, target):
    if not hasattr(target, '_skip_ft_index'):
        data = target.es_doc()
        data.pop('_id', None)
        Datastores.es.index(target.partition_id, 'report_group',
                            data, id=target.id)


def after_update(mapper, connection, target):
    if not hasattr(target, '_skip_ft_index'):
        data = target.es_doc()
        data.pop('_id', None)
        Datastores.es.index(target.partition_id, 'report_group',
                            data, id=target.id)


def after_delete(mapper, connection, target):
    query = {'term': {'group_id': target.id}}
    # TODO: routing seems unnecessary, need to test a bit more
    #Datastores.es.delete_by_query(target.partition_id, 'report', query,
    #                              query_params={'routing':str(target.id)})
    Datastores.es.delete_by_query(target.partition_id, 'report', query)
    query = {'term': {'pg_id': target.id}}
    Datastores.es.delete_by_query(target.partition_id, 'report_group', query)


sa.event.listen(ReportGroup, 'after_insert', after_insert)
sa.event.listen(ReportGroup, 'after_update', after_update)
sa.event.listen(ReportGroup, 'after_delete', after_delete)
