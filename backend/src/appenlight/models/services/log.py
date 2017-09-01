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

import paginate
import logging
import sqlalchemy as sa

from appenlight.models.log import Log
from appenlight.models import get_db_session, Datastores
from appenlight.models.services.base import BaseService
from appenlight.lib.utils import es_index_name_limiter

log = logging.getLogger(__name__)


class LogService(BaseService):
    @classmethod
    def get_logs(cls, resource_ids=None, filter_settings=None,
                 db_session=None):
        # ensure we always have id's passed
        if not resource_ids:
            # raise Exception('No App ID passed')
            return []
        db_session = get_db_session(db_session)
        q = db_session.query(Log)
        q = q.filter(Log.resource_id.in_(resource_ids))
        if filter_settings.get('start_date'):
            q = q.filter(Log.timestamp >= filter_settings.get('start_date'))
        if filter_settings.get('end_date'):
            q = q.filter(Log.timestamp <= filter_settings.get('end_date'))
        if filter_settings.get('log_level'):
            q = q.filter(
                Log.log_level == filter_settings.get('log_level').upper())
        if filter_settings.get('request_id'):
            request_id = filter_settings.get('request_id', '')
            q = q.filter(Log.request_id == request_id.replace('-', ''))
        if filter_settings.get('namespace'):
            q = q.filter(Log.namespace == filter_settings.get('namespace'))
        q = q.order_by(sa.desc(Log.timestamp))
        return q

    @classmethod
    def es_query_builder(cls, app_ids, filter_settings):
        if not filter_settings:
            filter_settings = {}

        query = {
            "query": {
                "filtered": {
                    "filter": {
                        "and": [{"terms": {"resource_id": list(app_ids)}}]
                    }
                }
            }
        }

        start_date = filter_settings.get('start_date')
        end_date = filter_settings.get('end_date')
        filter_part = query['query']['filtered']['filter']['and']

        for tag in filter_settings.get('tags', []):
            tag_values = [v.lower() for v in tag['value']]
            key = "tags.%s.values" % tag['name'].replace('.', '_')
            filter_part.append({"terms": {key: tag_values}})

        date_range = {"range": {"timestamp": {}}}
        if start_date:
            date_range["range"]["timestamp"]["gte"] = start_date
        if end_date:
            date_range["range"]["timestamp"]["lte"] = end_date
        if start_date or end_date:
            filter_part.append(date_range)

        levels = filter_settings.get('level')
        if levels:
            filter_part.append({"terms": {'log_level': levels}})
        namespaces = filter_settings.get('namespace')
        if namespaces:
            filter_part.append({"terms": {'namespace': namespaces}})

        request_ids = filter_settings.get('request_id')
        if request_ids:
            filter_part.append({"terms": {'request_id': request_ids}})

        messages = filter_settings.get('message')
        if messages:
            query['query']['filtered']['query'] = {
                'match': {
                    'message': {
                        'query': ' '.join(messages),
                        'operator': 'and'
                    }
                }
            }
        return query

    @classmethod
    def get_time_series_aggregate(cls, app_ids=None, filter_settings=None):
        if not app_ids:
            return {}
        es_query = cls.es_query_builder(app_ids, filter_settings)
        es_query["aggs"] = {
            "events_over_time": {
                "date_histogram": {
                    "field": "timestamp",
                    "interval": "1h",
                    "min_doc_count": 0,
                    'extended_bounds': {
                        'max': filter_settings.get('end_date'),
                        'min': filter_settings.get('start_date')}
                }
            }
        }
        log.debug(es_query)
        index_names = es_index_name_limiter(filter_settings.get('start_date'),
                                            filter_settings.get('end_date'),
                                            ixtypes=['logs'])
        if index_names:
            results = Datastores.es.search(
                es_query, index=index_names, doc_type='log', size=0)
        else:
            results = []
        return results

    @classmethod
    def get_search_iterator(cls, app_ids=None, page=1, items_per_page=50,
                            order_by=None, filter_settings=None, limit=None):
        if not app_ids:
            return {}, 0

        es_query = cls.es_query_builder(app_ids, filter_settings)
        sort_query = {
            "sort": [
                {"timestamp": {"order": "desc"}}
            ]
        }
        es_query.update(sort_query)
        log.debug(es_query)
        es_from = (page - 1) * items_per_page
        index_names = es_index_name_limiter(filter_settings.get('start_date'),
                                            filter_settings.get('end_date'),
                                            ixtypes=['logs'])
        if not index_names:
            return {}, 0

        results = Datastores.es.search(es_query, index=index_names,
                                       doc_type='log', size=items_per_page,
                                       es_from=es_from)
        if results['hits']['total'] > 5000:
            count = 5000
        else:
            count = results['hits']['total']
        return results['hits'], count

    @classmethod
    def get_paginator_by_app_ids(cls, app_ids=None, page=1, item_count=None,
                                 items_per_page=50, order_by=None,
                                 filter_settings=None,
                                 exclude_columns=None, db_session=None):
        if not filter_settings:
            filter_settings = {}
        results, item_count = cls.get_search_iterator(app_ids, page,
                                                      items_per_page, order_by,
                                                      filter_settings)
        paginator = paginate.Page([],
                                  item_count=item_count,
                                  items_per_page=items_per_page,
                                  **filter_settings)
        ordered_ids = tuple(item['_source']['pg_id']
                            for item in results.get('hits', []))

        sorted_instance_list = []
        if ordered_ids:
            db_session = get_db_session(db_session)
            query = db_session.query(Log)
            query = query.filter(Log.log_id.in_(ordered_ids))
            query = query.order_by(sa.desc('timestamp'))
            sa_items = query.all()
            # resort by score
            for i_id in ordered_ids:
                for item in sa_items:
                    if str(item.log_id) == str(i_id):
                        sorted_instance_list.append(item)
        paginator.sa_items = sorted_instance_list
        return paginator

    @classmethod
    def query_by_primary_key_and_namespace(cls, list_of_pairs,
                                           db_session=None):
        db_session = get_db_session(db_session)
        list_of_conditions = []
        query = db_session.query(Log)
        for pair in list_of_pairs:
            list_of_conditions.append(sa.and_(
                Log.primary_key == pair['pk'], Log.namespace == pair['ns']))
        query = query.filter(sa.or_(*list_of_conditions))
        query = query.order_by(sa.asc(Log.timestamp), sa.asc(Log.log_id))
        return query
