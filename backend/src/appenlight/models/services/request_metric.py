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

from datetime import datetime

import appenlight.lib.helpers as h
from appenlight.models import get_db_session, Datastores
from appenlight.models.services.base import BaseService
from appenlight.lib.enums import ReportType
from appenlight.lib.utils import es_index_name_limiter

try:
    from ae_uptime_ce.models.services.uptime_metric import UptimeMetricService
except ImportError:
    UptimeMetricService = None


def check_key(key, stats, uptime, total_seconds):
    if key not in stats:
        stats[key] = {
            "name": key,
            "requests": 0,
            "errors": 0,
            "tolerated_requests": 0,
            "frustrating_requests": 0,
            "satisfying_requests": 0,
            "total_minutes": total_seconds / 60.0,
            "uptime": uptime,
            "apdex": 0,
            "rpm": 0,
            "response_time": 0,
            "avg_response_time": 0,
        }


class RequestMetricService(BaseService):
    @classmethod
    def get_metrics_stats(cls, request, filter_settings, db_session=None):
        delta = filter_settings["end_date"] - filter_settings["start_date"]
        if delta < h.time_deltas.get("12h")["delta"]:
            interval = "1m"
        elif delta <= h.time_deltas.get("3d")["delta"]:
            interval = "5m"
        elif delta >= h.time_deltas.get("2w")["delta"]:
            interval = "24h"
        else:
            interval = "1h"

        filter_settings["namespace"] = ["appenlight.request_metric"]

        es_query = {
            "aggs": {
                "parent_agg": {
                    "aggs": {
                        "custom": {
                            "aggs": {
                                "sub_agg": {
                                    "sum": {"field": "tags.custom.numeric_values"}
                                }
                            },
                            "filter": {
                                "exists": {"field": "tags.custom.numeric_values"}
                            },
                        },
                        "main": {
                            "aggs": {
                                "sub_agg": {
                                    "sum": {"field": "tags.main.numeric_values"}
                                }
                            },
                            "filter": {"exists": {"field": "tags.main.numeric_values"}},
                        },
                        "nosql": {
                            "aggs": {
                                "sub_agg": {
                                    "sum": {"field": "tags.nosql.numeric_values"}
                                }
                            },
                            "filter": {
                                "exists": {"field": "tags.nosql.numeric_values"}
                            },
                        },
                        "remote": {
                            "aggs": {
                                "sub_agg": {
                                    "sum": {"field": "tags.remote.numeric_values"}
                                }
                            },
                            "filter": {
                                "exists": {"field": "tags.remote.numeric_values"}
                            },
                        },
                        "requests": {
                            "aggs": {
                                "sub_agg": {
                                    "sum": {"field": "tags.requests.numeric_values"}
                                }
                            },
                            "filter": {
                                "exists": {"field": "tags.requests.numeric_values"}
                            },
                        },
                        "sql": {
                            "aggs": {
                                "sub_agg": {"sum": {"field": "tags.sql.numeric_values"}}
                            },
                            "filter": {"exists": {"field": "tags.sql.numeric_values"}},
                        },
                        "tmpl": {
                            "aggs": {
                                "sub_agg": {
                                    "sum": {"field": "tags.tmpl.numeric_values"}
                                }
                            },
                            "filter": {"exists": {"field": "tags.tmpl.numeric_values"}},
                        },
                    },
                    "date_histogram": {
                        "extended_bounds": {
                            "max": filter_settings["end_date"],
                            "min": filter_settings["start_date"],
                        },
                        "field": "timestamp",
                        "interval": interval,
                        "min_doc_count": 0,
                    },
                }
            },
            "query": {
                "bool": {
                    "filter": [
                        {
                            "terms": {
                                "resource_id": [filter_settings["resource"][0]]
                            }
                        },
                        {
                            "range": {
                                "timestamp": {
                                    "gte": filter_settings["start_date"],
                                    "lte": filter_settings["end_date"],
                                }
                            }
                        },
                        {"terms": {"namespace": ["appenlight.request_metric"]}},
                    ]
                }
            },
        }

        index_names = es_index_name_limiter(
            start_date=filter_settings["start_date"],
            end_date=filter_settings["end_date"],
            ixtypes=["metrics"],
        )
        if not index_names:
            return []

        result = Datastores.es.search(
            body=es_query, index=index_names, doc_type="log", size=0
        )

        plot_data = []
        for item in result["aggregations"]["parent_agg"]["buckets"]:
            x_time = datetime.utcfromtimestamp(int(item["key"]) / 1000)
            point = {"x": x_time}
            for key in ["custom", "main", "nosql", "remote", "requests", "sql", "tmpl"]:
                value = item[key]["sub_agg"]["value"]
                point[key] = round(value, 3) if value else 0
            plot_data.append(point)

        return plot_data

    @classmethod
    def get_requests_breakdown(cls, request, filter_settings, db_session=None):
        db_session = get_db_session(db_session)

        # fetch total time of all requests in this time range
        index_names = es_index_name_limiter(
            start_date=filter_settings["start_date"],
            end_date=filter_settings["end_date"],
            ixtypes=["metrics"],
        )

        if index_names and filter_settings["resource"]:
            es_query = {
                "aggs": {
                    "main": {
                        "aggs": {
                            "sub_agg": {"sum": {"field": "tags.main.numeric_values"}}
                        },
                        "filter": {"exists": {"field": "tags.main.numeric_values"}},
                    }
                },
                "query": {
                    "bool": {
                        "filter": [
                            {
                                "terms": {
                                    "resource_id": [filter_settings["resource"][0]]
                                }
                            },
                            {
                                "range": {
                                    "timestamp": {
                                        "gte": filter_settings["start_date"],
                                        "lte": filter_settings["end_date"],
                                    }
                                }
                            },
                            {"terms": {"namespace": ["appenlight.request_metric"]}},
                        ]
                    }
                },
            }
            result = Datastores.es.search(
                body=es_query, index=index_names, doc_type="log", size=0
            )
            total_time_spent = result["aggregations"]["main"]["sub_agg"]["value"]
        else:
            total_time_spent = 0
        script_text = "doc['tags.main.numeric_values'].value / {}".format(
            total_time_spent
        )
        if total_time_spent == 0:
            script_text = '0'

        if index_names and filter_settings["resource"]:
            es_query = {
                "aggs": {
                    "parent_agg": {
                        "aggs": {
                            "main": {
                                "aggs": {
                                    "sub_agg": {
                                        "sum": {"field": "tags.main.numeric_values"}
                                    }
                                },
                                "filter": {
                                    "exists": {"field": "tags.main.numeric_values"}
                                },
                            },
                            "percentage": {
                                "aggs": {
                                    "sub_agg": {
                                        "sum": {
                                            "script": script_text,
                                        }
                                    }
                                },
                                "filter": {
                                    "exists": {"field": "tags.main.numeric_values"}
                                },
                            },
                            "requests": {
                                "aggs": {
                                    "sub_agg": {
                                        "sum": {"field": "tags.requests.numeric_values"}
                                    }
                                },
                                "filter": {
                                    "exists": {"field": "tags.requests.numeric_values"}
                                },
                            },
                        },
                        "terms": {
                            "field": "tags.view_name.values.keyword",
                            "order": {"percentage>sub_agg": "desc"},
                            "size": 15,
                        },
                    }
                },
                "query": {
                    "bool": {
                        "filter": [
                            {
                                "terms": {
                                    "resource_id": [filter_settings["resource"][0]]
                                }
                            },
                            {
                                "range": {
                                    "timestamp": {
                                        "gte": filter_settings["start_date"],
                                        "lte": filter_settings["end_date"],
                                    }
                                }
                            },
                        ]
                    }
                },
            }
            result = Datastores.es.search(
                body=es_query, index=index_names, doc_type="log", size=0
            )
            series = result["aggregations"]["parent_agg"]["buckets"]
        else:
            series = []

        and_part = [
            {"term": {"resource_id": filter_settings["resource"][0]}},
            {"terms": {"tags.view_name.values": [row["key"] for row in series]}},
            {"term": {"report_type": str(ReportType.slow)}},
        ]
        query = {
            "aggs": {
                "top_reports": {
                    "terms": {"field": "tags.view_name.values.keyword", "size": len(series)},
                    "aggs": {
                        "top_calls_hits": {
                            "top_hits": {"sort": {"start_time": "desc"}, "size": 5}
                        }
                    },
                }
            },
            "query": {"bool": {"filter": and_part}},
        }
        details = {}
        index_names = es_index_name_limiter(ixtypes=["reports"])
        if index_names and series:
            result = Datastores.es.search(
                body=query, doc_type="report", size=0, index=index_names
            )
            for bucket in result["aggregations"]["top_reports"]["buckets"]:
                details[bucket["key"]] = []

                for hit in bucket["top_calls_hits"]["hits"]["hits"]:
                    details[bucket["key"]].append(
                        {
                            "report_id": hit["_source"]["pg_id"],
                            "group_id": hit["_source"]["group_id"],
                        }
                    )

        results = []
        for row in series:
            result = {
                "key": row["key"],
                "main": row["main"]["sub_agg"]["value"],
                "requests": row["requests"]["sub_agg"]["value"],
            }
            # es can return 'infinity'
            try:
                result["percentage"] = float(row["percentage"]["sub_agg"]["value"])
            except ValueError:
                result["percentage"] = 0

            result["latest_details"] = details.get(row["key"]) or []
            results.append(result)

        return results

    @classmethod
    def get_apdex_stats(cls, request, filter_settings, threshold=1, db_session=None):
        """
        Returns information and calculates APDEX score per server for dashboard
        server information (upper right stats boxes)
        """
        # Apdex t = (Satisfied Count + Tolerated Count / 2) / Total Samples
        db_session = get_db_session(db_session)
        index_names = es_index_name_limiter(
            start_date=filter_settings["start_date"],
            end_date=filter_settings["end_date"],
            ixtypes=["metrics"],
        )

        requests_series = []

        if index_names and filter_settings["resource"]:
            es_query = {
                "aggs": {
                    "parent_agg": {
                        "aggs": {
                            "frustrating": {
                                "aggs": {
                                    "sub_agg": {
                                        "sum": {"field": "tags.requests.numeric_values"}
                                    }
                                },
                                "filter": {
                                    "bool": {
                                        "filter": [
                                            {
                                                "range": {
                                                    "tags.main.numeric_values": {"gte": "4"}
                                                }
                                            },
                                            {
                                                "exists": {
                                                    "field": "tags.requests.numeric_values"
                                                }
                                            },
                                        ]
                                    }
                                },
                            },
                            "main": {
                                "aggs": {
                                    "sub_agg": {
                                        "sum": {"field": "tags.main.numeric_values"}
                                    }
                                },
                                "filter": {
                                    "exists": {"field": "tags.main.numeric_values"}
                                },
                            },
                            "requests": {
                                "aggs": {
                                    "sub_agg": {
                                        "sum": {"field": "tags.requests.numeric_values"}
                                    }
                                },
                                "filter": {
                                    "exists": {"field": "tags.requests.numeric_values"}
                                },
                            },
                            "tolerated": {
                                "aggs": {
                                    "sub_agg": {
                                        "sum": {"field": "tags.requests.numeric_values"}
                                    }
                                },
                                "filter": {
                                    "bool": {"filter": [
                                        {
                                            "range": {
                                                "tags.main.numeric_values": {"gte": "1"}
                                            }
                                        },
                                        {
                                            "range": {
                                                "tags.main.numeric_values": {"lt": "4"}
                                            }
                                        },
                                        {
                                            "exists": {
                                                "field": "tags.requests.numeric_values"
                                            }
                                        },
                                    ]}
                                },
                            },
                        },
                        "terms": {"field": "tags.server_name.values.keyword", "size": 999999},
                    }
                },
                "query": {
                    "bool": {
                        "filter": [
                            {
                                "terms": {
                                    "resource_id": [filter_settings["resource"][0]]
                                }
                            },
                            {
                                "range": {
                                    "timestamp": {
                                        "gte": filter_settings["start_date"],
                                        "lte": filter_settings["end_date"],
                                    }
                                }
                            },
                            {"terms": {"namespace": ["appenlight.request_metric"]}},
                        ]
                    }
                },
            }

            result = Datastores.es.search(
                body=es_query, index=index_names, doc_type="log", size=0
            )
            for bucket in result["aggregations"]["parent_agg"]["buckets"]:
                requests_series.append(
                    {
                        "frustrating": bucket["frustrating"]["sub_agg"]["value"],
                        "main": bucket["main"]["sub_agg"]["value"],
                        "requests": bucket["requests"]["sub_agg"]["value"],
                        "tolerated": bucket["tolerated"]["sub_agg"]["value"],
                        "key": bucket["key"],
                    }
                )

        since_when = filter_settings["start_date"]
        until = filter_settings["end_date"]

        # total errors

        index_names = es_index_name_limiter(
            start_date=filter_settings["start_date"],
            end_date=filter_settings["end_date"],
            ixtypes=["reports"],
        )

        report_series = []
        if index_names and filter_settings["resource"]:
            report_type = ReportType.key_from_value(ReportType.error)
            es_query = {
                "aggs": {
                    "parent_agg": {
                        "aggs": {
                            "errors": {
                                "aggs": {
                                    "sub_agg": {
                                        "sum": {
                                            "field": "tags.occurences.numeric_values"
                                        }
                                    }
                                },
                                "filter": {
                                    "bool": {
                                        "filter": [
                                            {"terms": {"tags.type.values": [report_type]}},
                                            {
                                                "exists": {
                                                    "field": "tags.occurences.numeric_values"
                                                }
                                            },
                                        ]
                                    }
                                },
                            }
                        },
                        "terms": {"field": "tags.server_name.values.keyword", "size": 999999},
                    }
                },
                "query": {
                    "bool": {
                        "filter": [
                            {
                                "terms": {
                                    "resource_id": [filter_settings["resource"][0]]
                                }
                            },
                            {
                                "range": {
                                    "timestamp": {
                                        "gte": filter_settings["start_date"],
                                        "lte": filter_settings["end_date"],
                                    }
                                }
                            },
                            {"terms": {"namespace": ["appenlight.error"]}},
                        ]
                    }
                },
            }
            result = Datastores.es.search(
                body=es_query, index=index_names, doc_type="log", size=0
            )
            for bucket in result["aggregations"]["parent_agg"]["buckets"]:
                report_series.append(
                    {
                        "key": bucket["key"],
                        "errors": bucket["errors"]["sub_agg"]["value"],
                    }
                )

        stats = {}
        if UptimeMetricService is not None:
            uptime = UptimeMetricService.get_uptime_by_app(
                filter_settings["resource"][0], since_when=since_when, until=until
            )
        else:
            uptime = 0

        total_seconds = (until - since_when).total_seconds()

        for stat in requests_series:
            check_key(stat["key"], stats, uptime, total_seconds)
            stats[stat["key"]]["requests"] = int(stat["requests"])
            stats[stat["key"]]["response_time"] = stat["main"]
            stats[stat["key"]]["tolerated_requests"] = stat["tolerated"]
            stats[stat["key"]]["frustrating_requests"] = stat["frustrating"]
        for server in report_series:
            check_key(server["key"], stats, uptime, total_seconds)
            stats[server["key"]]["errors"] = server["errors"]

        server_stats = list(stats.values())
        for stat in server_stats:
            stat["satisfying_requests"] = (
                    stat["requests"]
                    - stat["errors"]
                    - stat["frustrating_requests"]
                    - stat["tolerated_requests"]
            )
            if stat["satisfying_requests"] < 0:
                stat["satisfying_requests"] = 0

            if stat["requests"]:
                stat["avg_response_time"] = round(
                    stat["response_time"] / stat["requests"], 3
                )
                qual_requests = (
                        stat["satisfying_requests"] + stat["tolerated_requests"] / 2.0
                )
                stat["apdex"] = round((qual_requests / stat["requests"]) * 100, 2)
                stat["rpm"] = round(stat["requests"] / stat["total_minutes"], 2)

        return sorted(server_stats, key=lambda x: x["name"])
