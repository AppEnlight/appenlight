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

from pyramid.view import view_config
from appenlight.models.services.plugin_config import PluginConfigService

import logging

log = logging.getLogger(__name__)


@view_config(route_name='plugin_configs', renderer='json',
             permission='edit', request_method='GET')
def query(request):
    configs = PluginConfigService.by_query(
        request.params.get('resource_id'),
        plugin_name=request.matchdict.get('plugin_name'),
        section=request.params.get('section'))
    return [c for c in configs]
