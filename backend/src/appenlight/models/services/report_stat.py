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

from appenlight.models import Datastores
from appenlight.models.services.base import BaseService
from appenlight.lib.enums import ReportType
from appenlight.lib.utils import es_index_name_limiter


class ReportStatService(BaseService):
    @classmethod
    def count_by_type(cls, report_type, resource_id, since_when):
        report_type = ReportType.key_from_value(report_type)

        index_names = es_index_name_limiter(start_date=since_when, ixtypes=["reports"])

        es_query = {
            "aggs": {
                "reports": {
                    "aggs": {
                        "sub_agg": {"value_count": {"field": "tags.group_id.values"}}
                    },
                    "filter": {
                        "bool": {
                            "filter": [
                                {"terms": {"resource_id": [resource_id]}},
                                {"exists": {"field": "tags.group_id.values"}},
                            ]
                        }
                    },
                }
            },
            "query": {
                "bool": {
                    "filter": [
                        {"terms": {"resource_id": [resource_id]}},
                        {"terms": {"tags.type.values": [report_type]}},
                        {"range": {"timestamp": {"gte": since_when}}},
                    ]
                }
            },
        }

        if index_names:
            result = Datastores.es.search(
                body=es_query, index=index_names, doc_type="log", size=0
            )
            return result["aggregations"]["reports"]["sub_agg"]["value"]
        else:
            return 0
