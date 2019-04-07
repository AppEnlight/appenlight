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

from appenlight.models import get_db_session, Datastores
from appenlight.models.report import Report
from appenlight.models.services.base import BaseService
from appenlight.lib.utils import es_index_name_limiter


class SlowCallService(BaseService):
    @classmethod
    def get_time_consuming_calls(cls, request, filter_settings, db_session=None):
        db_session = get_db_session(db_session)
        # get slow calls from older partitions too
        index_names = es_index_name_limiter(
            start_date=filter_settings["start_date"],
            end_date=filter_settings["end_date"],
            ixtypes=["slow_calls"],
        )
        if index_names and filter_settings["resource"]:
            # get longest time taking hashes
            es_query = {
                "aggs": {
                    "parent_agg": {
                        "aggs": {
                            "duration": {
                                "aggs": {
                                    "sub_agg": {
                                        "sum": {"field": "tags.duration.numeric_values"}
                                    }
                                },
                                "filter": {
                                    "exists": {"field": "tags.duration.numeric_values"}
                                },
                            },
                            "total": {
                                "aggs": {
                                    "sub_agg": {
                                        "value_count": {
                                            "field": "tags.statement_hash.values.keyword"
                                        }
                                    }
                                },
                                "filter": {
                                    "exists": {"field": "tags.statement_hash.values"}
                                },
                            },
                        },
                        "terms": {
                            "field": "tags.statement_hash.values.keyword",
                            "order": {"duration>sub_agg": "desc"},
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
            results = result["aggregations"]["parent_agg"]["buckets"]
        else:
            return []
        hashes = [i["key"] for i in results]

        # get queries associated with hashes
        calls_query = {
            "aggs": {
                "top_calls": {
                    "terms": {
                        "field": "tags.statement_hash.values.keyword",
                        "size": 15,
                    },
                    "aggs": {
                        "top_calls_hits": {
                            "top_hits": {"sort": {"timestamp": "desc"}, "size": 5}
                        }
                    },
                }
            },
            "query": {
                "bool": {
                    "filter": [
                        {"terms": {"resource_id": [filter_settings["resource"][0]]}},
                        {"terms": {"tags.statement_hash.values": hashes}},
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
        calls = Datastores.es.search(
            body=calls_query, index=index_names, doc_type="log", size=0
        )
        call_results = {}
        report_ids = []
        for call in calls["aggregations"]["top_calls"]["buckets"]:
            hits = call["top_calls_hits"]["hits"]["hits"]
            call_results[call["key"]] = [i["_source"] for i in hits]
            report_ids.extend(
                [i["_source"]["tags"]["report_id"]["values"] for i in hits]
            )
        if report_ids:
            r_query = db_session.query(Report.group_id, Report.id)
            r_query = r_query.filter(Report.id.in_(report_ids))
            r_query = r_query.filter(Report.start_time >= filter_settings["start_date"])
        else:
            r_query = []
        reports_reversed = {}
        for report in r_query:
            reports_reversed[report.id] = report.group_id

        final_results = []
        for item in results:
            if item["key"] not in call_results:
                continue
            call = call_results[item["key"]][0]
            row = {
                "occurences": item["total"]["sub_agg"]["value"],
                "total_duration": round(item["duration"]["sub_agg"]["value"]),
                "statement": call["message"],
                "statement_type": call["tags"]["type"]["values"],
                "statement_subtype": call["tags"]["subtype"]["values"],
                "statement_hash": item["key"],
                "latest_details": [],
            }
            if row["statement_type"] in ["tmpl", " remote"]:
                params = (
                    call["tags"]["parameters"]["values"]
                    if "parameters" in call["tags"]
                    else ""
                )
                row["statement"] = "{} ({})".format(call["message"], params)
            for call in call_results[item["key"]]:
                report_id = call["tags"]["report_id"]["values"]
                group_id = reports_reversed.get(report_id)
                if group_id:
                    row["latest_details"].append(
                        {"group_id": group_id, "report_id": report_id}
                    )

            final_results.append(row)

        return final_results
