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
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid import security
from appenlight.models.user import User

import logging

log = logging.getLogger(__name__)


@view_config(route_name='section_view', permission='root_administration',
             match_param=['section=admin_section', 'view=relogin_user'],
             renderer='json', request_method='GET')
def relogin_to_user(request):
    user = User.by_id(request.GET.get('user_id'))
    if not user:
        return HTTPNotFound()
    headers = security.remember(request, user.id)
    return HTTPFound(location=request.route_url('/'),
                     headers=headers)
