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

from appenlight.lib.helpers import gen_pagination_headers
from appenlight.models.services.event import EventService
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPBadRequest, HTTPNotFound
from ziggurat_foundations.models.services.user import UserService


@view_config(route_name="events_no_id", renderer="json", permission="authenticated")
def fetch_events(request):
    """
    Returns list of log entries from Elasticsearch
    """
    event_paginator = EventService.get_paginator(
        user=request.user, page=1, items_per_page=100
    )
    headers = gen_pagination_headers(request, event_paginator)
    request.response.headers.update(headers)

    return [ev.get_dict() for ev in event_paginator.items]


@view_config(
    route_name="events",
    renderer="json",
    request_method="PATCH",
    permission="authenticated",
)
def event_PATCH(request):
    resources = UserService.resources_with_perms(
        request.user, ["view"], resource_types=request.registry.resource_types
    )
    event = EventService.for_resource(
        [r.resource_id for r in resources], event_id=request.matchdict["event_id"]
    ).first()
    if not event:
        return HTTPNotFound()
    allowed_keys = ["status"]
    for k, v in request.unsafe_json_body.items():
        if k in allowed_keys:
            if k == "status":
                event.close()
            else:
                setattr(event, k, v)
        else:
            return HTTPBadRequest()
    return event.get_dict()
