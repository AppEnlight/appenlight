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

from pyramid.view import view_config
from appenlight.models.services.plugin_config import PluginConfigService

import logging

log = logging.getLogger(__name__)


@view_config(
    route_name="plugin_configs",
    renderer="json",
    permission="edit",
    request_method="GET",
)
def query(request):
    configs = PluginConfigService.by_query(
        request.params.get("resource_id"),
        plugin_name=request.matchdict.get("plugin_name"),
        section=request.params.get("section"),
    )
    return [c for c in configs]
