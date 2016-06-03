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

from pyramid.view import view_config
from appenlight.models import DBSession, Datastores
from appenlight.forms import get_partition_deletion_form

import logging

from zope.sqlalchemy import mark_changed
from datetime import datetime
import sqlalchemy as sa

log = logging.getLogger(__name__)


def get_partition_stats():
    table_query = """
        SELECT table_name
        FROM information_schema.tables
        GROUP BY table_name
        ORDER BY table_name
    """

    permanent_partitions = {}
    daily_partitions = {}

    def is_int(data):
        try:
            int(data)
            return True
        except Exception:
            pass
        return False

    def add_key(key, holder):
        if not ix_time in holder:
            holder[ix_time] = {'pg': [], 'elasticsearch': []}

    for partition in list(Datastores.es.aliases().keys()):
        if not partition.startswith('rcae'):
            continue
        split_data = partition.split('_')
        permanent = False
        # if we dont have a day then treat it as permanent partion
        if False in list(map(is_int, split_data[-3:])):
            ix_time = datetime(year=int(split_data[-2]),
                               month=int(split_data[-1]),
                               day=1).date()
            permanent = True
        else:
            ix_time = datetime(year=int(split_data[-3]),
                               month=int(split_data[-2]),
                               day=int(split_data[-1])).date()

        ix_time = str(ix_time)
        if permanent:
            add_key(ix_time, permanent_partitions)
            if ix_time not in permanent_partitions:
                permanent_partitions[ix_time]['elasticsearch'] = []
            permanent_partitions[ix_time]['elasticsearch'].append(partition)
        else:
            add_key(ix_time, daily_partitions)
            if ix_time not in daily_partitions:
                daily_partitions[ix_time]['elasticsearch'] = []
            daily_partitions[ix_time]['elasticsearch'].append(partition)

    for row in DBSession.execute(table_query):
        splitted = row['table_name'].split('_')
        if 'p' in splitted:
            # dealing with partition
            split_data = [int(x) for x in splitted[splitted.index('p') + 1:]]
            if len(split_data) == 3:
                ix_time = datetime(split_data[0], split_data[1],
                                   split_data[2]).date()
                ix_time = str(ix_time)
                add_key(ix_time, daily_partitions)
                daily_partitions[ix_time]['pg'].append(row['table_name'])
            else:
                ix_time = datetime(split_data[0], split_data[1], 1).date()
                ix_time = str(ix_time)
                add_key(ix_time, permanent_partitions)
                permanent_partitions[ix_time]['pg'].append(row['table_name'])

    return permanent_partitions, daily_partitions


@view_config(route_name='section_view', permission='root_administration',
             match_param=['section=admin_section', 'view=partitions'],
             renderer='json', request_method='GET')
def index(request):
    permanent_partitions, daily_partitions = get_partition_stats()

    return {"permanent_partitions": sorted(list(permanent_partitions.items()),
                                           key=lambda x: x[0], reverse=True),
            "daily_partitions": sorted(list(daily_partitions.items()),
                                       key=lambda x: x[0], reverse=True)}


@view_config(route_name='section_view', request_method='POST',
             match_param=['section=admin_section', 'view=partitions_remove'],
             renderer='json', permission='root_administration')
def partitions_remove(request):
    permanent_partitions, daily_partitions = get_partition_stats()
    pg_partitions = []
    es_partitions = []
    for item in list(permanent_partitions.values()) + list(daily_partitions.values()):
        es_partitions.extend(item['elasticsearch'])
        pg_partitions.extend(item['pg'])
    FormCls = get_partition_deletion_form(es_partitions, pg_partitions)
    form = FormCls(es_index=request.unsafe_json_body['es_indices'],
                   pg_index=request.unsafe_json_body['pg_indices'],
                   confirm=request.unsafe_json_body['confirm'],
                   csrf_context=request)
    if form.validate():
        for ix in form.data['es_index']:
            Datastores.es.delete_index(ix)
        for ix in form.data['pg_index']:
            stmt = sa.text('DROP TABLE %s CASCADE' % sa.text(ix))
            session = DBSession()
            session.connection().execute(stmt)
            mark_changed(session)

    for field, error in form.errors.items():
        msg = '%s: %s' % (field, error[0])
        request.session.flash(msg, 'error')

    permanent_partitions, daily_partitions = get_partition_stats()
    return {
        "permanent_partitions": sorted(
            list(permanent_partitions.items()), key=lambda x: x[0], reverse=True),
        "daily_partitions": sorted(
            list(daily_partitions.items()), key=lambda x: x[0], reverse=True)}
