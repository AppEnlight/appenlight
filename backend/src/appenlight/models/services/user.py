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
import pyramid_mailer
import pyramid.renderers
import sqlalchemy as sa

from collections import namedtuple
from datetime import datetime

from appenlight.lib.rule import Rule
from appenlight.models import get_db_session
from appenlight.models.integrations import IntegrationException
from appenlight.models.report import REPORT_TYPE_MATRIX
from appenlight.models.user import User
from appenlight.models.services.base import BaseService
from paginate_sqlalchemy import SqlalchemyOrmPage
from pyramid.threadlocal import get_current_registry

log = logging.getLogger(__name__)

GroupOccurence = namedtuple('GroupOccurence', ['occurences', 'group'])


class UserService(BaseService):
    @classmethod
    def all(cls, db_session=None):
        return get_db_session(db_session).query(User).order_by(User.user_name)

    @classmethod
    def send_email(cls, request, recipients, variables, template,
                   immediately=False, silent=False):
        html = pyramid.renderers.render(template, variables, request)
        title = variables.get('email_title',
                              variables.get('title', "No Title"))
        title = title.replace('\r', '').replace('\n', '')
        sender = "{} <{}>".format(
            request.registry.settings['mailing.from_name'],
            request.registry.settings['mailing.from_email'])
        message = pyramid_mailer.message.Message(
            subject=title, sender=sender, recipients=recipients, html=html)
        if immediately:
            try:
                request.registry.mailer.send_immediately(message)
            except Exception as e:
                log.warning('Exception %s' % e)
                if not silent:
                    raise
        else:
            request.registry.mailer.send(message)

    @classmethod
    def get_paginator(cls, page=1, item_count=None, items_per_page=50,
                      order_by=None, filter_settings=None,
                      exclude_columns=None, db_session=None):
        registry = get_current_registry()
        if not exclude_columns:
            exclude_columns = []
        if not filter_settings:
            filter_settings = {}
        db_session = get_db_session(db_session)
        q = db_session.query(User)
        if filter_settings.get('order_col'):
            order_col = filter_settings.get('order_col')
            if filter_settings.get('order_dir') == 'dsc':
                sort_on = 'desc'
            else:
                sort_on = 'asc'
            q = q.order_by(getattr(sa, sort_on)(getattr(User, order_col)))
        else:
            q = q.order_by(sa.desc(User.registered_date))
            # remove urlgen or it never caches count
        cache_params = dict(filter_settings)
        cache_params.pop('url', None)
        cache_params.pop('url_maker', None)

        @registry.cache_regions.redis_min_5.cache_on_arguments()
        def estimate_users(cache_key):
            o_q = q.order_by(False)
            return o_q.count()

        item_count = estimate_users(cache_params)
        # if the number of pages is low we may want to invalidate the count to
        # provide 'real time' update - use case -
        # errors just started to flow in
        if item_count < 1000:
            item_count = estimate_users.refresh(cache_params)
        paginator = SqlalchemyOrmPage(q, page=page,
                                      item_count=item_count,
                                      items_per_page=items_per_page,
                                      **filter_settings)
        return paginator

    @classmethod
    def get_valid_channels(cls, user):
        return [channel for channel in user.alert_channels
                if channel.channel_validated]

    @classmethod
    def report_notify(cls, user, request, application, report_groups,
                      occurence_dict, db_session=None):
        db_session = get_db_session(db_session)
        if not report_groups:
            return True
        since_when = datetime.utcnow()
        for channel in cls.get_valid_channels(user):
            confirmed_groups = []

            for group in report_groups:
                occurences = occurence_dict.get(group.id, 1)
                for action in channel.channel_actions:
                    not_matched = (
                        action.resource_id and action.resource_id !=
                        application.resource_id)
                    if action.type != 'report' or not_matched:
                        continue
                    should_notify = (action.action == 'always' or
                                     not group.notified)
                    rule_obj = Rule(action.rule, REPORT_TYPE_MATRIX)
                    report_dict = group.get_report().get_dict(request)
                    if rule_obj.match(report_dict) and should_notify:
                        item = GroupOccurence(occurences, group)
                        if item not in confirmed_groups:
                            confirmed_groups.append(item)

            # send individual reports
            total_confirmed = len(confirmed_groups)
            if not total_confirmed:
                continue
            try:
                channel.notify_reports(resource=application,
                                       user=user,
                                       request=request,
                                       since_when=since_when,
                                       reports=confirmed_groups)
            except IntegrationException as e:
                log.warning('%s' % e)
