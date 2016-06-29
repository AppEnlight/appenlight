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

from appenlight.lib.helpers import gen_pagination_headers
from appenlight.models.services.event import EventService
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPBadRequest, HTTPNotFound


@view_config(route_name='events_no_id',
             renderer='json', permission='authenticated')
def fetch_events(request):
    """
    Returns list of log entries from Elasticsearch
    """
    event_paginator = EventService.get_paginator(
        user=request.user,
        page=1,
        items_per_page=100
    )
    headers = gen_pagination_headers(request, event_paginator)
    request.response.headers.update(headers)

    return [ev.get_dict() for ev in event_paginator.items]


@view_config(route_name='events', renderer='json', request_method='PATCH',
             permission='authenticated')
def event_PATCH(request):
    resources = request.user.resources_with_perms(
        ['view'], resource_types=request.registry.resource_types)
    event = EventService.for_resource(
        [r.resource_id for r in resources],
        event_id=request.matchdict['event_id']).first()
    if not event:
        return HTTPNotFound()
    allowed_keys = ['status']
    for k, v in request.unsafe_json_body.items():
        if k in allowed_keys:
            if k == 'status':
                event.close()
            else:
                setattr(event, k, v)
        else:
            return HTTPBadRequest()
    return event.get_dict()
