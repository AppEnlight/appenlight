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

import logging
from datetime import datetime, timedelta

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPUnprocessableEntity
from appenlight.models import Datastores, Log
from appenlight.models.services.log import LogService
from appenlight.lib.utils import (build_filter_settings_from_query_dict,
                                  es_index_name_limiter)
from appenlight.lib.helpers import gen_pagination_headers
from appenlight.celery.tasks import logs_cleanup

log = logging.getLogger(__name__)

section_filters_key = 'appenlight:logs:filter:%s'


@view_config(route_name='logs_no_id', renderer='json',
             permission='authenticated')
def fetch_logs(request):
    """
    Returns list of log entries from Elasticsearch
    """

    filter_settings = build_filter_settings_from_query_dict(request,
                                                            request.GET.mixed())
    logs_paginator = LogService.get_paginator_by_app_ids(
        app_ids=filter_settings['resource'],
        page=filter_settings['page'],
        filter_settings=filter_settings
    )
    headers = gen_pagination_headers(request, logs_paginator)
    request.response.headers.update(headers)

    return [l.get_dict() for l in logs_paginator.sa_items]


@view_config(route_name='section_view',
             match_param=['section=logs_section', 'view=fetch_series'],
             renderer='json', permission='authenticated')
def logs_fetch_series(request):
    """
    Handles metric dashboard graphs
    Returns information for time/tier breakdown
    """
    filter_settings = build_filter_settings_from_query_dict(request,
                                                            request.GET.mixed())
    paginator = LogService.get_paginator_by_app_ids(
        app_ids=filter_settings['resource'],
        page=1, filter_settings=filter_settings, items_per_page=1)
    now = datetime.utcnow().replace(microsecond=0, second=0)
    delta = timedelta(days=7)
    if paginator.sa_items:
        start_date = paginator.sa_items[-1].timestamp.replace(microsecond=0,
                                                              second=0)
        filter_settings['start_date'] = start_date - delta
    else:
        filter_settings['start_date'] = now - delta
    filter_settings['end_date'] = filter_settings['start_date'] \
                                  + timedelta(days=7)
    since_when = filter_settings['start_date']

    @request.registry.cache_regions.redis_sec_30.cache_on_arguments(
        'logs_graphs')
    def cached(apps, search_params, delta, now):
        data = LogService.get_time_series_aggregate(
            filter_settings['resource'], filter_settings)
        if not data:
            return []
        buckets = data['aggregations']['events_over_time']['buckets']
        return [{"x": datetime.utcfromtimestamp(item["key"] / 1000),
                 "logs": item["doc_count"]} for item in buckets]

    return cached(filter_settings, request.GET.mixed(), delta, now)


@view_config(route_name='logs_no_id', renderer='json', request_method="DELETE",
             permission='authenticated')
def logs_mass_delete(request):
    params = request.GET.mixed()
    if 'resource' not in params:
        raise HTTPUnprocessableEntity()
    # this might be '' and then colander will not validate the schema
    if not params.get('namespace'):
        params.pop('namespace', None)
    filter_settings = build_filter_settings_from_query_dict(
        request, params, resource_permissions=['update_reports'])

    resource_id = list(filter_settings['resource'])[0]
    # filter settings returns list of all of users applications
    # if app is not matching - normally we would not care as its used for search
    # but here user playing with params would possibly wipe out their whole data
    if int(resource_id) != int(params['resource']):
        raise HTTPUnprocessableEntity()

    logs_cleanup.delay(resource_id, filter_settings)
    msg = 'Log cleanup process started - it may take a while for ' \
          'everything to get removed'
    request.session.flash(msg)
    return {}


@view_config(route_name='section_view',
             match_param=("view=common_tags", "section=logs_section"),
             renderer='json', permission='authenticated')
def common_tags(request):
    config = request.GET.mixed()
    filter_settings = build_filter_settings_from_query_dict(request,
                                                            config)

    resources = list(filter_settings["resource"])
    query = {
        "query": {
            "filtered": {
                "filter": {
                    "and": [{"terms": {"resource_id": list(resources)}}]
                }
            }
        }
    }
    start_date = filter_settings.get('start_date')
    end_date = filter_settings.get('end_date')
    filter_part = query['query']['filtered']['filter']['and']

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

    query["aggs"] = {
        "sub_agg": {
            "terms": {
                "field": "tag_list",
                "size": 50
            }
        }
    }
    # tags
    index_names = es_index_name_limiter(
        ixtypes=[config.get('datasource', 'logs')])
    result = Datastores.es.search(query, index=index_names, doc_type='log',
                                  size=0)
    tag_buckets = result['aggregations']['sub_agg'].get('buckets', [])
    # namespaces
    query["aggs"] = {
        "sub_agg": {
            "terms": {
                "field": "namespace",
                "size": 50
            }
        }
    }
    result = Datastores.es.search(query, index=index_names, doc_type='log',
                                  size=0)
    namespaces_buckets = result['aggregations']['sub_agg'].get('buckets', [])
    return {
        "tags": [item['key'] for item in tag_buckets],
        "namespaces": [item['key'] for item in namespaces_buckets]
    }


@view_config(route_name='section_view',
             match_param=("view=common_values", "section=logs_section"),
             renderer='json', permission='authenticated')
def common_values(request):
    config = request.GET.mixed()
    datasource = config.pop('datasource', 'logs')
    filter_settings = build_filter_settings_from_query_dict(request,
                                                            config)
    resources = list(filter_settings["resource"])
    tag_name = filter_settings['tags'][0]['value'][0]
    query = {
        'query': {
            'filtered': {
                'filter': {
                    'and': [
                        {'terms': {'resource_id': list(resources)}},
                        {'terms': {
                            'namespace': filter_settings['namespace']}}
                    ]
                }
            }
        }
    }
    query['aggs'] = {
        'sub_agg': {
            'terms': {
                'field': 'tags.{}.values'.format(tag_name),
                'size': 50
            }
        }
    }
    index_names = es_index_name_limiter(ixtypes=[datasource])
    result = Datastores.es.search(query, index=index_names, doc_type='log',
                                  size=0)
    values_buckets = result['aggregations']['sub_agg'].get('buckets', [])
    return {
        "values": [item['key'] for item in values_buckets]
    }
