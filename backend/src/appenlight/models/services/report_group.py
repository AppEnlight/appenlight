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
import paginate
import sqlalchemy as sa
import appenlight.lib.helpers as h

from datetime import datetime

from appenlight.models import get_db_session, Datastores
from appenlight.models.report import Report
from appenlight.models.report_group import ReportGroup
from appenlight.models.report_comment import ReportComment
from appenlight.models.user import User
from appenlight.models.services.base import BaseService
from appenlight.lib.enums import ReportType
from appenlight.lib.utils import es_index_name_limiter

log = logging.getLogger(__name__)


class ReportGroupService(BaseService):
    @classmethod
    def get_trending(cls, request, filter_settings, limit=15,
                     db_session=None):
        """
        Returns report groups trending for specific time interval
        """
        db_session = get_db_session(db_session)

        tags = []
        if filter_settings.get('tags'):
            for tag in filter_settings['tags']:
                tags.append(
                    {'terms': {
                        'tags.{}.values'.format(tag['name']): tag['value']}})

        index_names = es_index_name_limiter(
            start_date=filter_settings['start_date'],
            end_date=filter_settings['end_date'],
            ixtypes=['reports'])

        if not index_names or not filter_settings['resource']:
            return []

        es_query = {
            'aggs': {'parent_agg': {'aggs': {'groups': {'aggs': {
                'sub_agg': {
                    'value_count': {'field': 'tags.group_id.values'}}},
                'filter': {'exists': {'field': 'tags.group_id.values'}}}},
                'terms': {'field': 'tags.group_id.values', 'size': limit}}},
            'query': {'filtered': {
                'filter': {'and': [
                    {'terms': {
                        'resource_id': [filter_settings['resource'][0]]}
                    },
                    {'range': {'timestamp': {
                        'gte': filter_settings['start_date'],
                        'lte': filter_settings['end_date']}}}]
                }
            }}
        }
        if tags:
            es_query['query']['filtered']['filter']['and'].extend(tags)

        result = Datastores.es.search(
            body=es_query, index=index_names, doc_type='log', size=0)
        series = []
        for bucket in result['aggregations']['parent_agg']['buckets']:
            series.append({
                'key': bucket['key'],
                'groups': bucket['groups']['sub_agg']['value']
            })

        report_groups_d = {}
        for g in series:
            report_groups_d[int(g['key'])] = g['groups'] or 0

        query = db_session.query(ReportGroup)
        query = query.filter(ReportGroup.id.in_(list(report_groups_d.keys())))
        query = query.options(
            sa.orm.joinedload(ReportGroup.last_report_ref))
        results = [(report_groups_d[group.id], group,) for group in query]
        return sorted(results, reverse=True, key=lambda x:x[0])

    @classmethod
    def get_search_iterator(cls, app_ids=None, page=1, items_per_page=50,
                            order_by=None, filter_settings=None, limit=None):
        if not app_ids:
            return {}
        if not filter_settings:
            filter_settings = {}

        query = {
            "size": 0,
            "query": {
                "filtered": {
                    "filter": {
                        "and": [{"terms": {"resource_id": list(app_ids)}}]
                    }
                }
            },

            "aggs": {
                "top_groups": {
                    "terms": {
                        "size": 5000,
                        "field": "_parent",
                        "order": {
                            "newest": "desc"
                        }
                    },
                    "aggs": {
                        "top_reports_hits": {
                            "top_hits": {"size": 1,
                                         "sort": {"start_time": "desc"}
                                         }
                        },
                        "newest": {
                            "max": {"field": "start_time"}
                        }
                    }
                }
            }
        }

        start_date = filter_settings.get('start_date')
        end_date = filter_settings.get('end_date')
        filter_part = query['query']['filtered']['filter']['and']
        date_range = {"range": {"start_time": {}}}
        if start_date:
            date_range["range"]["start_time"]["gte"] = start_date
        if end_date:
            date_range["range"]["start_time"]["lte"] = end_date
        if start_date or end_date:
            filter_part.append(date_range)

        priorities = filter_settings.get('priority')

        for tag in filter_settings.get('tags', []):
            tag_values = [v.lower() for v in tag['value']]
            key = "tags.%s.values" % tag['name'].replace('.', '_')
            filter_part.append({"terms": {key: tag_values}})

        if priorities:
            filter_part.append({"has_parent": {
                "parent_type": "report_group",
                "query": {
                    "terms": {'priority': priorities}
                }}})

        min_occurences = filter_settings.get('min_occurences')
        if min_occurences:
            filter_part.append({"has_parent": {
                "parent_type": "report_group",
                "query": {
                    "range": {'occurences': {"gte": min_occurences[0]}}
                }}})

        min_duration = filter_settings.get('min_duration')
        max_duration = filter_settings.get('max_duration')

        request_ids = filter_settings.get('request_id')
        if request_ids:
            filter_part.append({"terms": {'request_id': request_ids}})

        duration_range = {"range": {"average_duration": {}}}
        if min_duration:
            duration_range["range"]["average_duration"]["gte"] = \
                min_duration[0]
        if max_duration:
            duration_range["range"]["average_duration"]["lte"] = \
                max_duration[0]
        if min_duration or max_duration:
            filter_part.append({"has_parent": {
                "parent_type": "report_group",
                "query": duration_range}})

        http_status = filter_settings.get('http_status')
        report_type = filter_settings.get('report_type', [ReportType.error])
        # set error report type if http status is not found
        # and we are dealing with slow reports
        if not http_status or ReportType.slow in report_type:
            filter_part.append({"terms": {'report_type': report_type}})
        if http_status:
            filter_part.append({"terms": {'http_status': http_status}})

        messages = filter_settings.get('message')
        if messages:
            condition = {'match': {"message": ' '.join(messages)}}
            query['query']['filtered']['query'] = condition
        errors = filter_settings.get('error')
        if errors:
            condition = {'match': {"error": ' '.join(errors)}}
            query['query']['filtered']['query'] = condition
        url_domains = filter_settings.get('url_domain')
        if url_domains:
            condition = {'terms': {"url_domain": url_domains}}
            query['query']['filtered']['query'] = condition
        url_paths = filter_settings.get('url_path')
        if url_paths:
            condition = {'terms': {"url_path": url_paths}}
            query['query']['filtered']['query'] = condition

        if filter_settings.get('report_status'):
            for status in filter_settings.get('report_status'):
                if status == 'never_reviewed':
                    filter_part.append({"has_parent": {
                        "parent_type": "report_group",
                        "query": {
                            "term": {"read": False}
                        }}})
                elif status == 'reviewed':
                    filter_part.append({"has_parent": {
                        "parent_type": "report_group",
                        "query": {
                            "term": {"read": True}
                        }}})
                elif status == 'public':
                    filter_part.append({"has_parent": {
                        "parent_type": "report_group",
                        "query": {
                            "term": {"public": True}
                        }}})
                elif status == 'fixed':
                    filter_part.append({"has_parent": {
                        "parent_type": "report_group",
                        "query": {
                            "term": {"fixed": True}
                        }}})

        # logging.getLogger('pyelasticsearch').setLevel(logging.DEBUG)
        index_names = es_index_name_limiter(filter_settings.get('start_date'),
                                            filter_settings.get('end_date'),
                                            ixtypes=['reports'])
        if index_names:
            results = Datastores.es.search(
                body=query, index=index_names, doc_type=["report", "report_group"],
                size=0)
        else:
            return []
        return results['aggregations']

    @classmethod
    def get_paginator_by_app_ids(cls, app_ids=None, page=1, item_count=None,
                                 items_per_page=50, order_by=None,
                                 filter_settings=None,
                                 exclude_columns=None, db_session=None):
        if not filter_settings:
            filter_settings = {}
        results = cls.get_search_iterator(app_ids, page, items_per_page,
                                          order_by, filter_settings)

        ordered_ids = []
        if results:
            for item in results['top_groups']['buckets']:
                pg_id = item['top_reports_hits']['hits']['hits'][0]['_source'][
                    'pg_id']
                ordered_ids.append(pg_id)
        log.info(filter_settings)
        paginator = paginate.Page(ordered_ids, items_per_page=items_per_page,
                                  **filter_settings)
        sa_items = ()
        if paginator.items:
            db_session = get_db_session(db_session)
            # latest report detail
            query = db_session.query(Report)
            query = query.options(sa.orm.joinedload(Report.report_group))
            query = query.filter(Report.id.in_(paginator.items))
            if filter_settings.get('order_col'):
                order_col = filter_settings.get('order_col')
                if filter_settings.get('order_dir') == 'dsc':
                    sort_on = 'desc'
                else:
                    sort_on = 'asc'
                if order_col == 'when':
                    order_col = 'last_timestamp'
                query = query.order_by(getattr(sa, sort_on)(
                    getattr(ReportGroup, order_col)))
            sa_items = query.all()
        sorted_instance_list = []
        for i_id in ordered_ids:
            for report in sa_items:
                if (str(report.id) == i_id and
                            report not in sorted_instance_list):
                    sorted_instance_list.append(report)
        paginator.sa_items = sorted_instance_list
        return paginator

    @classmethod
    def by_app_ids(cls, app_ids=None, order_by=True, db_session=None):
        db_session = get_db_session(db_session)
        q = db_session.query(ReportGroup)
        if app_ids:
            q = q.filter(ReportGroup.resource_id.in_(app_ids))
        if order_by:
            q = q.order_by(sa.desc(ReportGroup.id))
        return q

    @classmethod
    def by_id(cls, group_id, app_ids=None, db_session=None):
        db_session = get_db_session(db_session)
        q = db_session.query(ReportGroup).filter(
            ReportGroup.id == int(group_id))
        if app_ids:
            q = q.filter(ReportGroup.resource_id.in_(app_ids))
        return q.first()

    @classmethod
    def by_ids(cls, group_ids=None, db_session=None):
        db_session = get_db_session(db_session)
        query = db_session.query(ReportGroup)
        query = query.filter(ReportGroup.id.in_(group_ids))
        return query

    @classmethod
    def by_hash_and_resource(cls, resource_id, grouping_hash, since_when=None,
                             db_session=None):
        db_session = get_db_session(db_session)
        q = db_session.query(ReportGroup)
        q = q.filter(ReportGroup.resource_id == resource_id)
        q = q.filter(ReportGroup.grouping_hash == grouping_hash)
        q = q.filter(ReportGroup.fixed == False)
        if since_when:
            q = q.filter(ReportGroup.first_timestamp >= since_when)
        return q.first()

    @classmethod
    def users_commenting(cls, report_group, exclude_user_id=None,
                         db_session=None):
        db_session = get_db_session(None, report_group)
        query = db_session.query(User).distinct()
        query = query.filter(User.id == ReportComment.owner_id)
        query = query.filter(ReportComment.group_id == report_group.id)
        if exclude_user_id:
            query = query.filter(ReportComment.owner_id != exclude_user_id)
        return query

    @classmethod
    def affected_users_count(cls, report_group, db_session=None):
        db_session = get_db_session(db_session)
        query = db_session.query(sa.func.count(Report.username))
        query = query.filter(Report.group_id == report_group.id)
        query = query.filter(Report.username != '')
        query = query.filter(Report.username != None)
        query = query.group_by(Report.username)
        return query.count()

    @classmethod
    def top_affected_users(cls, report_group, db_session=None):
        db_session = get_db_session(db_session)
        count_label = sa.func.count(Report.username).label('count')
        query = db_session.query(Report.username, count_label)
        query = query.filter(Report.group_id == report_group.id)
        query = query.filter(Report.username != None)
        query = query.filter(Report.username != '')
        query = query.group_by(Report.username)
        query = query.order_by(sa.desc(count_label))
        query = query.limit(50)
        return query

    @classmethod
    def get_report_stats(cls, request, filter_settings):
        """
        Gets report dashboard graphs
        Returns information for BAR charts with occurences/interval information
        detailed means version that returns time intervals - non detailed
        returns total sum
        """
        delta = filter_settings['end_date'] - filter_settings['start_date']
        if delta < h.time_deltas.get('12h')['delta']:
            interval = '1m'
        elif delta <= h.time_deltas.get('3d')['delta']:
            interval = '5m'
        elif delta >= h.time_deltas.get('2w')['delta']:
            interval = '24h'
        else:
            interval = '1h'

        group_id = filter_settings.get('group_id')

        es_query = {
            'aggs': {'parent_agg': {'aggs': {'types': {
                'aggs': {'sub_agg': {'terms': {'field': 'tags.type.values'}}},
                'filter': {
                    'and': [{'exists': {'field': 'tags.type.values'}}]}
            }},
                'date_histogram': {'extended_bounds': {
                    'max': filter_settings['end_date'],
                    'min': filter_settings['start_date']},
                    'field': 'timestamp',
                    'interval': interval,
                    'min_doc_count': 0}}},
            'query': {'filtered': {
                'filter': {'and': [
                    {'terms': {
                        'resource_id': [filter_settings['resource'][0]]}},
                    {'range': {'timestamp': {
                        'gte': filter_settings['start_date'],
                        'lte': filter_settings['end_date']}}}]
                }
            }}
        }
        if group_id:
            parent_agg = es_query['aggs']['parent_agg']
            filters = parent_agg['aggs']['types']['filter']['and']
            filters.append({'terms': {'tags.group_id.values': [group_id]}})

        index_names = es_index_name_limiter(
            start_date=filter_settings['start_date'],
            end_date=filter_settings['end_date'],
            ixtypes=['reports'])

        if not index_names:
            return []

        result = Datastores.es.search(body=es_query,
                                      index=index_names,
                                      doc_type='log',
                                      size=0)
        series = []
        for bucket in result['aggregations']['parent_agg']['buckets']:
            point = {
                'x': datetime.utcfromtimestamp(int(bucket['key']) / 1000),
                'report': 0,
                'not_found': 0,
                'slow_report': 0
            }
            for subbucket in bucket['types']['sub_agg']['buckets']:
                if subbucket['key'] == 'slow':
                    point['slow_report'] = subbucket['doc_count']
                elif subbucket['key'] == 'error':
                    point['report'] = subbucket['doc_count']
                elif subbucket['key'] == 'not_found':
                    point['not_found'] = subbucket['doc_count']
            series.append(point)
        return series
