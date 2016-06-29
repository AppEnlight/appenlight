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

from appenlight.models import Datastores
from appenlight.models.services.base import BaseService
from appenlight.lib.enums import ReportType
from appenlight.lib.utils import es_index_name_limiter


class ReportStatService(BaseService):
    @classmethod
    def count_by_type(cls, report_type, resource_id, since_when):
        report_type = ReportType.key_from_value(report_type)

        index_names = es_index_name_limiter(start_date=since_when,
                              ixtypes=['reports'])

        es_query = {
            'aggs': {'reports': {'aggs': {
                'sub_agg': {'value_count': {'field': 'tags.group_id.values'}}},
                'filter': {'and': [{'terms': {'resource_id': [resource_id]}},
                                   {'exists': {
                                       'field': 'tags.group_id.values'}}]}}},
            'query': {'filtered': {'filter': {
                'and': [{'terms': {'resource_id': [resource_id]}},
                        {'terms': {'tags.type.values': [report_type]}},
                        {'range': {'timestamp': {
                            'gte': since_when}}}]}}}}

        if index_names:
            result = Datastores.es.search(es_query,
                                      index=index_names,
                                      doc_type='log',
                                      size=0)
            return result['aggregations']['reports']['sub_agg']['value']
        else:
            return 0
