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

    for partition in list(Datastores.es.indices.get_alias('rcae*')):
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
            log.warning('deleting ES partition: {}'.format(ix))
            Datastores.es.indices.delete(ix)
        for ix in form.data['pg_index']:
            log.warning('deleting PG partition: {}'.format(ix))
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
