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

import argparse
import datetime
import logging
import copy

import sqlalchemy as sa
import elasticsearch.exceptions
import elasticsearch.helpers

from collections import defaultdict
from pyramid.paster import setup_logging
from pyramid.paster import bootstrap
from appenlight.models import DBSession, Datastores, metadata
from appenlight.lib import get_callable
from appenlight.models.report_group import ReportGroup
from appenlight.models.report import Report
from appenlight.models.report_stat import ReportStat
from appenlight.models.log import Log
from appenlight.models.slow_call import SlowCall
from appenlight.models.metric import Metric

log = logging.getLogger(__name__)

tables = {
    "slow_calls_p_": [],
    "reports_stats_p_": [],
    "reports_p_": [],
    "reports_groups_p_": [],
    "logs_p_": [],
    "metrics_p_": [],
}


def detect_tables(table_prefix):
    found_tables = []
    db_tables_query = """
    SELECT tablename FROM pg_tables WHERE tablename NOT LIKE 'pg_%' AND
    tablename NOT LIKE 'sql_%' ORDER BY tablename ASC;"""

    for table in DBSession.execute(db_tables_query).fetchall():
        tablename = table.tablename
        if tablename.startswith(table_prefix):
            t = sa.Table(
                tablename, metadata, autoload=True, autoload_with=DBSession.bind.engine
            )
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
        description="Reindex AppEnlight data", add_help=False
    )
    pre_parser.add_argument(
        "-c", "--config", required=True, help="Configuration ini file of application"
    )
    pre_parser.add_argument("-h", "--help", help="Show help", nargs="?")
    pre_parser.add_argument(
        "-t", "--types", nargs="+", help="Which parts of database should get reindexed"
    )
    args = pre_parser.parse_args()

    config_uri = args.config
    setup_logging(config_uri)
    log.setLevel(logging.INFO)
    env = bootstrap(config_uri)
    parser = argparse.ArgumentParser(description="Reindex AppEnlight data")
    choices = {
        "reports": "appenlight.scripts.reindex_elasticsearch:reindex_reports",
        "logs": "appenlight.scripts.reindex_elasticsearch:reindex_logs",
        "metrics": "appenlight.scripts.reindex_elasticsearch:reindex_metrics",
        "slow_calls": "appenlight.scripts.reindex_elasticsearch:reindex_slow_calls",
        "template": "appenlight.scripts.reindex_elasticsearch:update_template",
    }
    for k, v in env["registry"].appenlight_plugins.items():
        if v.get("fulltext_indexer"):
            choices[k] = v["fulltext_indexer"]
    parser.add_argument(
        "-t",
        "--types",
        nargs="*",
        choices=["all"] + list(choices.keys()),
        default=[],
        help="Which parts of database should get reindexed",
    )
    parser.add_argument(
        "-c", "--config", required=True, help="Configuration ini file of application"
    )
    args = parser.parse_args()

    if "all" in args.types:
        args.types = list(choices.keys())

    print("Selected types to reindex: {}".format(args.types))

    log.info("settings {}".format(args.types))

    if "template" in args.types:
        get_callable(choices["template"])()
        args.types.remove("template")
    for selected in args.types:
        get_callable(choices[selected])()


def update_template():
    try:
        Datastores.es.indices.delete_template("rcae_reports")
    except elasticsearch.exceptions.NotFoundError as e:
        log.error(e)

    try:
        Datastores.es.indices.delete_template("rcae_logs")
    except elasticsearch.exceptions.NotFoundError as e:
        log.error(e)
    try:
        Datastores.es.indices.delete_template("rcae_slow_calls")
    except elasticsearch.exceptions.NotFoundError as e:
        log.error(e)
    try:
        Datastores.es.indices.delete_template("rcae_metrics")
    except elasticsearch.exceptions.NotFoundError as e:
        log.error(e)
    log.info("updating elasticsearch template")
    tag_templates = [
        {
            "values": {
                "path_match": "tags.*",
                "mapping": {
                    "type": "object",
                    "properties": {
                        "values": {"type": "text", "analyzer": "tag_value",
                                   "fields": {
                                       "keyword": {
                                           "type": "keyword",
                                           "ignore_above": 256
                                       }
                                   }},
                        "numeric_values": {"type": "float"},
                    },
                },
            }
        }
    ]

    shared_analysis = {
        "analyzer": {
            "url_path": {
                "type": "custom",
                "char_filter": [],
                "tokenizer": "path_hierarchy",
                "filter": [],
            },
            "tag_value": {
                "type": "custom",
                "char_filter": [],
                "tokenizer": "keyword",
                "filter": ["lowercase"],
            },
        }
    }

    shared_log_mapping = {
        "_all": {"enabled": False},
        "dynamic_templates": tag_templates,
        "properties": {
            "pg_id": {"type": "keyword", "index": True},
            "delete_hash": {"type": "keyword", "index": True},
            "resource_id": {"type": "integer"},
            "timestamp": {"type": "date"},
            "permanent": {"type": "boolean"},
            "request_id": {"type": "keyword", "index": True},
            "log_level": {"type": "text", "analyzer": "simple"},
            "message": {"type": "text", "analyzer": "simple"},
            "namespace": {
                "type": "text",
                "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
            },
            "tags": {"type": "object"},
            "tag_list": {"type": "text", "analyzer": "tag_value",
                         "fields": {
                             "keyword": {
                                 "type": "keyword",
                                 "ignore_above": 256
                             }
                         }},
        },
    }

    report_schema = {
        "template": "rcae_r_*",
        "settings": {
            "index": {
                "refresh_interval": "5s",
                "translog": {"sync_interval": "5s", "durability": "async"},
                "mapping": {"single_type": True}
            },
            "number_of_shards": 5,
            "analysis": shared_analysis,
        },
        "mappings": {
            "report": {
                "_all": {"enabled": False},
                "dynamic_templates": tag_templates,
                "properties": {
                    "type": {"type": "keyword", "index": True},
                    # report group
                    "group_id": {"type": "keyword", "index": True},
                    "resource_id": {"type": "integer"},
                    "priority": {"type": "integer"},
                    "error": {"type": "text", "analyzer": "simple"},
                    "read": {"type": "boolean"},
                    "occurences": {"type": "integer"},
                    "fixed": {"type": "boolean"},
                    "first_timestamp": {"type": "date"},
                    "last_timestamp": {"type": "date"},
                    "average_duration": {"type": "float"},
                    "summed_duration": {"type": "float"},
                    "public": {"type": "boolean"},
                    # report

                    "report_id": {"type": "keyword", "index": True},
                    "http_status": {"type": "integer"},
                    "ip": {"type": "keyword", "index": True},
                    "url_domain": {"type": "text", "analyzer": "simple"},
                    "url_path": {"type": "text", "analyzer": "url_path"},
                    "report_type": {"type": "integer"},
                    "start_time": {"type": "date"},
                    "request_id": {"type": "keyword", "index": True},
                    "end_time": {"type": "date"},
                    "duration": {"type": "float"},
                    "tags": {"type": "object"},
                    "tag_list": {"type": "text", "analyzer": "tag_value",
                                 "fields": {
                                     "keyword": {
                                         "type": "keyword",
                                         "ignore_above": 256
                                     }
                                 }},
                    "extra": {"type": "object"},

                    # report stats

                    "report_stat_id": {"type": "keyword", "index": True},
                    "timestamp": {"type": "date"},
                    "permanent": {"type": "boolean"},
                    "log_level": {"type": "text", "analyzer": "simple"},
                    "message": {"type": "text", "analyzer": "simple"},
                    "namespace": {
                        "type": "text",
                        "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
                    },

                    "join_field": {
                        "type": "join",
                        "relations": {
                            "report_group": ["report", "report_stat"]
                        }
                    }

                },
            }
        }
    }

    Datastores.es.indices.put_template("rcae_reports", body=report_schema)

    logs_mapping = copy.deepcopy(shared_log_mapping)
    logs_mapping["properties"]["log_id"] = logs_mapping["properties"]["pg_id"]
    del logs_mapping["properties"]["pg_id"]

    log_template = {
        "template": "rcae_l_*",
        "settings": {
            "index": {
                "refresh_interval": "5s",
                "translog": {"sync_interval": "5s", "durability": "async"},
                "mapping": {"single_type": True}
            },
            "number_of_shards": 5,
            "analysis": shared_analysis,
        },
        "mappings": {
            "log": logs_mapping,
        },
    }

    Datastores.es.indices.put_template("rcae_logs", body=log_template)

    slow_call_mapping = copy.deepcopy(shared_log_mapping)
    slow_call_mapping["properties"]["slow_call_id"] = slow_call_mapping["properties"]["pg_id"]
    del slow_call_mapping["properties"]["pg_id"]

    slow_call_template = {
        "template": "rcae_sc_*",
        "settings": {
            "index": {
                "refresh_interval": "5s",
                "translog": {"sync_interval": "5s", "durability": "async"},
                "mapping": {"single_type": True}
            },
            "number_of_shards": 5,
            "analysis": shared_analysis,
        },
        "mappings": {
            "log": slow_call_mapping,
        },
    }

    Datastores.es.indices.put_template("rcae_slow_calls", body=slow_call_template)

    metric_mapping = copy.deepcopy(shared_log_mapping)
    metric_mapping["properties"]["metric_id"] = metric_mapping["properties"]["pg_id"]
    del metric_mapping["properties"]["pg_id"]

    metrics_template = {
        "template": "rcae_m_*",
        "settings": {
            "index": {
                "refresh_interval": "5s",
                "translog": {"sync_interval": "5s", "durability": "async"},
                "mapping": {"single_type": True}
            },
            "number_of_shards": 5,
            "analysis": shared_analysis,
        },
        "mappings": {
            "log": metric_mapping,
        },
    }

    Datastores.es.indices.put_template("rcae_metrics", body=metrics_template)

    uptime_metric_mapping = copy.deepcopy(shared_log_mapping)
    uptime_metric_mapping["properties"]["uptime_id"] = uptime_metric_mapping["properties"]["pg_id"]
    del uptime_metric_mapping["properties"]["pg_id"]

    uptime_metrics_template = {
        "template": "rcae_uptime_ce_*",
        "settings": {
            "index": {
                "refresh_interval": "5s",
                "translog": {"sync_interval": "5s", "durability": "async"},
                "mapping": {"single_type": True}
            },
            "number_of_shards": 5,
            "analysis": shared_analysis,
        },
        "mappings": {
            "log": shared_log_mapping,
        },
    }

    Datastores.es.indices.put_template("rcae_uptime_metrics", body=uptime_metrics_template)


def reindex_reports():
    reports_groups_tables = detect_tables("reports_groups_p_")
    try:
        Datastores.es.indices.delete("`rcae_r_*")
    except elasticsearch.exceptions.NotFoundError as e:
        log.error(e)

    log.info("reindexing report groups")
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
                log.info("round {}, {}".format(i, name))
                for k, v in es_docs.items():
                    to_update = {"_index": k, "_type": "report"}
                    [i.update(to_update) for i in v]
                    elasticsearch.helpers.bulk(Datastores.es, v)

    log.info("total docs {} {}".format(i, datetime.datetime.now() - task_start))

    i = 0
    log.info("reindexing reports")
    task_start = datetime.datetime.now()
    reports_tables = detect_tables("reports_p_")
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
                log.info("round {}, {}".format(i, name))
                for k, v in es_docs.items():
                    to_update = {"_index": k, "_type": "report"}
                    [i.update(to_update) for i in v]
                    elasticsearch.helpers.bulk(Datastores.es, v)

    log.info("total docs {} {}".format(i, datetime.datetime.now() - task_start))

    log.info("reindexing reports stats")
    i = 0
    task_start = datetime.datetime.now()
    reports_stats_tables = detect_tables("reports_stats_p_")
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
                rd.pop("size", None)
                item = ReportStat(**rd)
                i += 1
                d_range = item.partition_id
                es_docs[d_range].append(item.es_doc())
            if es_docs:
                name = partition_table.name
                log.info("round  {}, {}".format(i, name))
                for k, v in es_docs.items():
                    to_update = {"_index": k, "_type": "report"}
                    [i.update(to_update) for i in v]
                    elasticsearch.helpers.bulk(Datastores.es, v)

    log.info("total docs {} {}".format(i, datetime.datetime.now() - task_start))


def reindex_logs():
    try:
        Datastores.es.indices.delete("rcae_l_*")
    except elasticsearch.exceptions.NotFoundError as e:
        log.error(e)

    # logs
    log.info("reindexing logs")
    i = 0
    task_start = datetime.datetime.now()
    log_tables = detect_tables("logs_p_")
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
                log.info("round  {}, {}".format(i, name))
                for k, v in es_docs.items():
                    to_update = {"_index": k, "_type": "log"}
                    [i.update(to_update) for i in v]
                    elasticsearch.helpers.bulk(Datastores.es, v)

    log.info("total docs {} {}".format(i, datetime.datetime.now() - task_start))


def reindex_metrics():
    try:
        Datastores.es.indices.delete("rcae_m_*")
    except elasticsearch.exceptions.NotFoundError as e:
        log.error(e)

    log.info("reindexing applications metrics")
    i = 0
    task_start = datetime.datetime.now()
    metric_tables = detect_tables("metrics_p_")
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
                log.info("round  {}, {}".format(i, name))
                for k, v in es_docs.items():
                    to_update = {"_index": k, "_type": "log"}
                    [i.update(to_update) for i in v]
                    elasticsearch.helpers.bulk(Datastores.es, v)

    log.info("total docs {} {}".format(i, datetime.datetime.now() - task_start))


def reindex_slow_calls():
    try:
        Datastores.es.indices.delete("rcae_sc_*")
    except elasticsearch.exceptions.NotFoundError as e:
        log.error(e)

    log.info("reindexing slow calls")
    i = 0
    task_start = datetime.datetime.now()
    slow_calls_tables = detect_tables("slow_calls_p_")
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
                log.info("round  {}, {}".format(i, name))
                for k, v in es_docs.items():
                    to_update = {"_index": k, "_type": "log"}
                    [i.update(to_update) for i in v]
                    elasticsearch.helpers.bulk(Datastores.es, v)

    log.info("total docs {} {}".format(i, datetime.datetime.now() - task_start))


if __name__ == "__main__":
    main()
