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

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPNotFound
from appenlight.models.services.config import ConfigService

import logging

log = logging.getLogger(__name__)


@view_config(route_name='admin_configs', renderer='json',
             permission='root_administration', request_method='GET')
def query(request):
    ConfigService.setup_default_values()
    pairs = []
    for value in request.GET.getall('filter'):
        split = value.split(':', 1)
        pairs.append({'key': split[0], 'section': split[1]})
    return [c for c in ConfigService.filtered_key_and_section(pairs)]


@view_config(route_name='admin_config', renderer='json',
             permission='root_administration', request_method='POST')
def post(request):
    row = ConfigService.by_key_and_section(
        key=request.matchdict.get('key'),
        section=request.matchdict.get('section'))
    if not row:
        raise HTTPNotFound()
    row.value = None
    row.value = request.unsafe_json_body['value']
    return row
