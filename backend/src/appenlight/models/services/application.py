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
import urllib.parse

import sqlalchemy as sa
from pyramid.threadlocal import get_current_request

from appenlight.lib.cache_regions import get_region
from appenlight.lib.enums import ReportType
from appenlight.models import get_db_session
from appenlight.models.report_group import ReportGroup
from appenlight.models.application import Application
from appenlight.models.event import Event
from appenlight.models.services.base import BaseService
from appenlight.models.services.event import EventService

log = logging.getLogger(__name__)


class ApplicationService(BaseService):

    @classmethod
    def all(cls, db_session=None):
        db_session = get_db_session(db_session)
        q = db_session.query(Application)
        return q

    @classmethod
    def by_api_key(cls, api_key, db_session=None):
        db_session = get_db_session(db_session)
        q = db_session.query(Application)
        q = q.filter(Application.api_key == api_key)
        q = q.options(sa.orm.eagerload(Application.owner))
        return q.first()

    @classmethod
    def by_api_key_cached(cls, db_session=None):
        db_session = get_db_session(db_session)
        cache_region = get_region('redis_min_1')

        @cache_region.cache_on_arguments('ApplicationService.by_api_key')
        def cached(*args, **kwargs):
            app = cls.by_api_key(*args, db_session=db_session, **kwargs)
            if app:
                db_session.expunge(app)
            return app

        return cached

    @classmethod
    def by_public_api_key(cls, api_key, db_session=None, from_cache=False,
                          request=None):
        db_session = get_db_session(db_session)
        cache_region = get_region('redis_min_1')

        def uncached(api_key):
            q = db_session.query(Application)
            q = q.filter(Application.public_key == api_key)
            q = q.options(sa.orm.eagerload(Application.owner))
            return q.first()

        if from_cache:
            @cache_region.cache_on_arguments(
                'ApplicationService.by_public_api_key')
            def cached(api_key):
                app = uncached(api_key)
                if app:
                    db_session.expunge(app)
                return app

            app = cached(api_key)
        else:
            app = uncached(api_key)
        return app

    @classmethod
    def by_id(cls, db_id, db_session=None):
        db_session = get_db_session(db_session)
        q = db_session.query(Application)
        q = q.filter(Application.resource_id == db_id)
        return q.first()

    @classmethod
    def by_id_cached(cls, db_session=None):
        db_session = get_db_session(db_session)
        cache_region = get_region('redis_min_1')

        @cache_region.cache_on_arguments('ApplicationService.by_id')
        def cached(*args, **kwargs):
            app = cls.by_id(*args, db_session=db_session, **kwargs)
            if app:
                db_session.expunge(app)
            return app

        return cached

    @classmethod
    def by_ids(cls, db_ids, db_session=None):
        db_session = get_db_session(db_session)
        query = db_session.query(Application)
        query = query.filter(Application.resource_id.in_(db_ids))
        return query

    @classmethod
    def by_http_referer(cls, referer_string, db_session=None):
        db_session = get_db_session(db_session)
        domain = urllib.parse.urlsplit(
            referer_string, allow_fragments=False).netloc
        if domain:
            if domain.startswith('www.'):
                domain = domain[4:]
        q = db_session.query(Application).filter(Application.domain == domain)
        return q.first()

    @classmethod
    def last_updated(cls, since_when, exclude_status=None, db_session=None):
        db_session = get_db_session(db_session)
        q = db_session.query(Application)
        q2 = ReportGroup.last_updated(
            since_when, exclude_status=exclude_status, db_session=db_session)
        q2 = q2.from_self(ReportGroup.resource_id)
        q2 = q2.group_by(ReportGroup.resource_id)
        q = q.filter(Application.resource_id.in_(q2))
        return q

    @classmethod
    def check_for_groups_alert(cls, resource, event_type, *args, **kwargs):
        """ Check for open alerts depending on group type.
        Create new one if nothing is found and send alerts """
        db_session = get_db_session(kwargs.get('db_session'))
        request = get_current_request()
        report_groups = kwargs['report_groups']
        occurence_dict = kwargs['occurence_dict']

        error_reports = 0
        slow_reports = 0
        for group in report_groups:
            occurences = occurence_dict.get(group.id, 1)
            if group.get_report().report_type == ReportType.error:
                error_reports += occurences
            elif group.get_report().report_type == ReportType.slow:
                slow_reports += occurences

        log_msg = 'LIMIT INFO: %s : %s error reports. %s slow_reports' % (
            resource,
            error_reports,
            slow_reports)
        logging.warning(log_msg)
        threshold = 10
        for event_type in ['error_report_alert', 'slow_report_alert']:
            if (error_reports < resource.error_report_threshold and
                        event_type == 'error_report_alert'):
                continue
            elif (slow_reports <= resource.slow_report_threshold and
                          event_type == 'slow_report_alert'):
                continue
            if event_type == 'error_report_alert':
                amount = error_reports
                threshold = resource.error_report_threshold
            elif event_type == 'slow_report_alert':
                amount = slow_reports
                threshold = resource.slow_report_threshold

            event = EventService.for_resource([resource.resource_id],
                                              event_type=Event.types[
                                                  event_type],
                                              status=Event.statuses['active'])
            if event.first():
                log.info('ALERT: PROGRESS: %s %s' % (event_type, resource))
            else:
                log.warning('ALERT: OPEN: %s %s' % (event_type, resource))
                new_event = Event(resource_id=resource.resource_id,
                                  event_type=Event.types[event_type],
                                  status=Event.statuses['active'],
                                  values={'reports': amount,
                                          'threshold': threshold})
                db_session.add(new_event)
                new_event.send_alerts(request=request, resource=resource)
