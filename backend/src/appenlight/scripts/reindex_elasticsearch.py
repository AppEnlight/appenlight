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

import argparse
import datetime
import logging

import sqlalchemy as sa
from collections import defaultdict
from pyramid.paster import setup_logging
from pyramid.paster import bootstrap
from appenlight.models import (
    DBSession,
    Datastores,
    metadata
)
from appenlight.lib import get_callable
from appenlight.models.report_group import ReportGroup
from appenlight.models.report import Report
from appenlight.models.report_stat import ReportStat
from appenlight.models.log import Log
from appenlight.models.slow_call import SlowCall
from appenlight.models.request_metric import Metric


log = logging.getLogger(__name__)

tables = {
    'slow_calls_p_': [],
    'reports_stats_p_': [],
    'reports_p_': [],
    'reports_groups_p_': [],
    'logs_p_': [],
    'metrics_p_': [],
}

def detect_tables(table_prefix):
    found_tables = []
    db_tables_query = '''
    SELECT tablename FROM pg_tables WHERE tablename NOT LIKE 'pg_%' AND
    tablename NOT LIKE 'sql_%' ORDER BY tablename ASC;'''

    for table in DBSession.execute(db_tables_query).fetchall():
        tablename = table.tablename
        if tablename.startswith(table_prefix):
            t = sa.Table(tablename, metadata, autoload=True,
                         autoload_with=DBSession.bind.engine)
            found_tables.append(t)
    return found_tables


def main():
    """
    Recreates Elasticsearch indexes
    Performs reindex of whole db to Elasticsearch

    """

    # need parser twice because we first need to load ini file
    # bootstrap pyramid and then load plugins
    pre_parser = argparse.ArgumentParser(
        description='Reindex AppEnlight data',
        add_help=False)
    pre_parser.add_argument('-c', '--config', required=True,
                            help='Configuration ini file of application')
    pre_parser.add_argument('-h', '--help', help='Show help', nargs='?')
    pre_parser.add_argument('-t', '--types', nargs='+',
                            help='Which parts of database should get reindexed')
    args = pre_parser.parse_args()

    config_uri = args.config
    setup_logging(config_uri)
    log.setLevel(logging.INFO)
    env = bootstrap(config_uri)
    parser = argparse.ArgumentParser(description='Reindex AppEnlight data')
    choices = {
        'reports': 'appenlight.scripts.reindex_elasticsearch:reindex_reports',
        'logs': 'appenlight.scripts.reindex_elasticsearch:reindex_logs',
        'metrics': 'appenlight.scripts.reindex_elasticsearch:reindex_metrics',
        'slow_calls': 'appenlight.scripts.reindex_elasticsearch:reindex_slow_calls',
        'template': 'appenlight.scripts.reindex_elasticsearch:update_template'
    }
    for k, v in env['registry'].appenlight_plugins.items():
        if v.get('fulltext_indexer'):
            choices[k] = v['fulltext_indexer']
    parser.add_argument('-t', '--types', nargs='*',
                        choices=['all'] + list(choices.keys()), default=['all'],
                        help='Which parts of database should get reindexed')
    parser.add_argument('-c', '--config', required=True,
                        help='Configuration ini file of application')
    args = parser.parse_args()


    if 'all' in args.types:
        args.types = list(choices.keys())

    log.info('settings {}'.format(args.types))

    if 'template' in args.types:
        get_callable(choices['template'])()
        args.types.remove('template')
    for selected in args.types:
        get_callable(choices[selected])()


def update_template():
    try:
        Datastores.es.send_request("delete", ['_template', 'rcae'],
                                   query_params={})
    except Exception as e:
        print(e)
    log.info('updating elasticsearch template')
    tag_templates = [
        {"values": {
            "path_match": "tags.*",
            "mapping": {
                "type": "object",
                "properties": {
                    "values": {"type": "string", "analyzer": "tag_value"},
                    "numeric_values": {"type": "float"}
                }
            }
        }}
    ]

    template_schema = {
        "template": "rcae_*",
        "settings": {
            "index": {
                "refresh_interval": "5s",
                "translog": {"interval": "5s",
                             "durability": "async"}
            },
            "number_of_shards": 5,
            "analysis": {
                "analyzer": {
                    "url_path": {
                        "type": "custom",
                        "char_filter": [],
                        "tokenizer": "path_hierarchy",
                        "filter": []
                    },
                    "tag_value": {
                        "type": "custom",
                        "char_filter": [],
                        "tokenizer": "keyword",
                        "filter": ["lowercase"]
                    },
                }
            },
        },
        "mappings": {
            "report_group": {
                "_all": {"enabled": False},
                "dynamic_templates": tag_templates,
                "properties": {
                    "pg_id": {"type": "string", "index": "not_analyzed"},
                    "resource_id": {"type": "integer"},
                    "priority": {"type": "integer"},
                    "error": {"type": "string", "analyzer": "simple"},
                    "read": {"type": "boolean"},
                    "occurences": {"type": "integer"},
                    "fixed": {"type": "boolean"},
                    "first_timestamp": {"type": "date"},
                    "last_timestamp": {"type": "date"},
                    "average_duration": {"type": "float"},
                    "summed_duration": {"type": "float"},
                    "public": {"type": "boolean"}
                }
            },
            "report": {
                "_all": {"enabled": False},
                "dynamic_templates": tag_templates,
                "properties": {
                    "pg_id": {"type": "string", "index": "not_analyzed"},
                    "resource_id": {"type": "integer"},
                    "group_id": {"type": "string"},
                    "http_status": {"type": "integer"},
                    "ip": {"type": "string", "index": "not_analyzed"},
                    "url_domain": {"type": "string", "analyzer": "simple"},
                    "url_path": {"type": "string", "analyzer": "url_path"},
                    "error": {"type": "string", "analyzer": "simple"},
                    "report_type": {"type": "integer"},
                    "start_time": {"type": "date"},
                    "request_id": {"type": "string", "index": "not_analyzed"},
                    "end_time": {"type": "date"},
                    "duration": {"type": "float"},
                    "tags": {
                        "type": "object"
                    },
                    "tag_list": {"type": "string", "analyzer": "tag_value"},
                    "extra": {
                        "type": "object"
                    },
                },
                "_parent": {"type": "report_group"}
            },
            "log": {
                "_all": {"enabled": False},
                "dynamic_templates": tag_templates,
                "properties": {
                    "pg_id": {"type": "string", "index": "not_analyzed"},
                    "delete_hash": {"type": "string", "index": "not_analyzed"},
                    "resource_id": {"type": "integer"},
                    "timestamp": {"type": "date"},
                    "permanent": {"type": "boolean"},
                    "request_id": {"type": "string", "index": "not_analyzed"},
                    "log_level": {"type": "string", "analyzer": "simple"},
                    "message": {"type": "string", "analyzer": "simple"},
                    "namespace": {"type": "string", "index": "not_analyzed"},
                    "tags": {
                        "type": "object"
                    },
                    "tag_list": {"type": "string", "analyzer": "tag_value"}
                }
            }
        }
    }

    Datastores.es.send_request('PUT', ['_template', 'rcae'],
                               body=template_schema, query_params={})


def reindex_reports():
    reports_groups_tables = detect_tables('reports_groups_p_')
    try:
        Datastores.es.delete_index('rcae_r*')
    except Exception as e:
        log.error(e)

    log.info('reindexing report groups')
    i = 0
    task_start = datetime.datetime.now()
    for partition_table in reports_groups_tables:
        conn = DBSession.connection().execution_options(stream_results=True)
        result = conn.execute(partition_table.select())
        while True:
            chunk = result.fetchmany(2000)
            if not chunk:
                break
            es_docs = defaultdict(list)
            for row in chunk:
                i += 1
                item = ReportGroup(**dict(list(row.items())))
                d_range = item.partition_id
                es_docs[d_range].append(item.es_doc())
            if es_docs:
                name = partition_table.name
                log.info('round {}, {}'.format(i, name))
                for k, v in es_docs.items():
                    Datastores.es.bulk_index(k, 'report_group', v,
                                             id_field="_id")

    log.info(
        'total docs {} {}'.format(i, datetime.datetime.now() - task_start))

    i = 0
    log.info('reindexing reports')
    task_start = datetime.datetime.now()
    reports_tables = detect_tables('reports_p_')
    for partition_table in reports_tables:
        conn = DBSession.connection().execution_options(stream_results=True)
        result = conn.execute(partition_table.select())
        while True:
            chunk = result.fetchmany(2000)
            if not chunk:
                break
            es_docs = defaultdict(list)
            for row in chunk:
                i += 1
                item = Report(**dict(list(row.items())))
                d_range = item.partition_id
                es_docs[d_range].append(item.es_doc())
            if es_docs:
                name = partition_table.name
                log.info('round {}, {}'.format(i, name))
                for k, v in es_docs.items():
                    Datastores.es.bulk_index(k, 'report', v, id_field="_id",
                                             parent_field='_parent')

    log.info(
        'total docs {} {}'.format(i, datetime.datetime.now() - task_start))

    log.info('reindexing reports stats')
    i = 0
    task_start = datetime.datetime.now()
    reports_stats_tables = detect_tables('reports_stats_p_')
    for partition_table in reports_stats_tables:
        conn = DBSession.connection().execution_options(stream_results=True)
        result = conn.execute(partition_table.select())
        while True:
            chunk = result.fetchmany(2000)
            if not chunk:
                break
            es_docs = defaultdict(list)
            for row in chunk:
                rd = dict(list(row.items()))
                # remove legacy columns
                # TODO: remove the column later
                rd.pop('size', None)
                item = ReportStat(**rd)
                i += 1
                d_range = item.partition_id
                es_docs[d_range].append(item.es_doc())
            if es_docs:
                name = partition_table.name
                log.info('round  {}, {}'.format(i, name))
                for k, v in es_docs.items():
                    Datastores.es.bulk_index(k, 'log', v)

    log.info(
        'total docs {} {}'.format(i, datetime.datetime.now() - task_start))


def reindex_logs():
    try:
        Datastores.es.delete_index('rcae_l*')
    except Exception as e:
        log.error(e)

    # logs
    log.info('reindexing logs')
    i = 0
    task_start = datetime.datetime.now()
    log_tables = detect_tables('logs_p_')
    for partition_table in log_tables:
        conn = DBSession.connection().execution_options(stream_results=True)
        result = conn.execute(partition_table.select())
        while True:
            chunk = result.fetchmany(2000)
            if not chunk:
                break
            es_docs = defaultdict(list)

            for row in chunk:
                i += 1
                item = Log(**dict(list(row.items())))
                d_range = item.partition_id
                es_docs[d_range].append(item.es_doc())
            if es_docs:
                name = partition_table.name
                log.info('round  {}, {}'.format(i, name))
                for k, v in es_docs.items():
                    Datastores.es.bulk_index(k, 'log', v)

    log.info(
        'total docs {} {}'.format(i, datetime.datetime.now() - task_start))


def reindex_metrics():
    try:
        Datastores.es.delete_index('rcae_m*')
    except Exception as e:
        print(e)

    log.info('reindexing applications metrics')
    i = 0
    task_start = datetime.datetime.now()
    metric_tables = detect_tables('metrics_p_')
    for partition_table in metric_tables:
        conn = DBSession.connection().execution_options(stream_results=True)
        result = conn.execute(partition_table.select())
        while True:
            chunk = result.fetchmany(2000)
            if not chunk:
                break
            es_docs = defaultdict(list)
            for row in chunk:
                i += 1
                item = Metric(**dict(list(row.items())))
                d_range = item.partition_id
                es_docs[d_range].append(item.es_doc())
            if es_docs:
                name = partition_table.name
                log.info('round  {}, {}'.format(i, name))
                for k, v in es_docs.items():
                    Datastores.es.bulk_index(k, 'log', v)

    log.info(
        'total docs {} {}'.format(i, datetime.datetime.now() - task_start))


def reindex_slow_calls():
    try:
        Datastores.es.delete_index('rcae_sc*')
    except Exception as e:
        print(e)

    log.info('reindexing slow calls')
    i = 0
    task_start = datetime.datetime.now()
    slow_calls_tables = detect_tables('slow_calls_p_')
    for partition_table in slow_calls_tables:
        conn = DBSession.connection().execution_options(stream_results=True)
        result = conn.execute(partition_table.select())
        while True:
            chunk = result.fetchmany(2000)
            if not chunk:
                break
            es_docs = defaultdict(list)
            for row in chunk:
                i += 1
                item = SlowCall(**dict(list(row.items())))
                d_range = item.partition_id
                es_docs[d_range].append(item.es_doc())
            if es_docs:
                name = partition_table.name
                log.info('round  {}, {}'.format(i, name))
                for k, v in es_docs.items():
                    Datastores.es.bulk_index(k, 'log', v)

    log.info(
        'total docs {} {}'.format(i, datetime.datetime.now() - task_start))


if __name__ == '__main__':
    main()
