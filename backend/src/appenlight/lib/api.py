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

import datetime
import logging

from pyramid.httpexceptions import HTTPForbidden, HTTPTooManyRequests

from appenlight.models import Datastores
from appenlight.models.services.config import ConfigService
from appenlight.lib.redis_keys import REDIS_KEYS

log = logging.getLogger(__name__)


def rate_limiting(request, resource, section, to_increment=1):
    tsample = datetime.datetime.utcnow().replace(second=0, microsecond=0)
    key = REDIS_KEYS['rate_limits'][section].format(tsample,
                                                    resource.resource_id)
    redis_pipeline = request.registry.redis_conn.pipeline()
    redis_pipeline.incr(key, to_increment)
    redis_pipeline.expire(key, 3600 * 24)
    results = redis_pipeline.execute()
    current_count = results[0]
    config = ConfigService.by_key_and_section(section, 'global')
    limit = config.value if config else 1000
    if current_count > int(limit):
        log.info('RATE LIMITING: {}: {}, {}'.format(
            section, resource, current_count))
        abort_msg = 'Rate limits are in effect for this application'
        raise HTTPTooManyRequests(abort_msg,
                                  headers={'X-AppEnlight': abort_msg})


def check_cors(request, application, should_return=True):
    """
    Performs a check and validation if request comes from authorized domain for
    application, otherwise return 403
    """
    origin_found = False
    origin = request.headers.get('Origin')
    if should_return:
        log.info('CORS for %s' % origin)
    if not origin:
        return False
    for domain in application.domains.split('\n'):
        if domain in origin:
            origin_found = True
    if origin_found:
        request.response.headers.add('Access-Control-Allow-Origin', origin)
        request.response.headers.add('XDomainRequestAllowed', '1')
        request.response.headers.add('Access-Control-Allow-Methods',
                                     'GET, POST, OPTIONS')
        request.response.headers.add('Access-Control-Allow-Headers',
                                     'Accept-Encoding, Accept-Language, '
                                     'Content-Type, '
                                     'Depth, User-Agent, X-File-Size, '
                                     'X-Requested-With, If-Modified-Since, '
                                     'X-File-Name, '
                                     'Cache-Control, Host, Pragma, Accept, '
                                     'Origin, Connection, '
                                     'Referer, Cookie, '
                                     'X-appenlight-public-api-key, '
                                     'x-appenlight-public-api-key')
        request.response.headers.add('Access-Control-Max-Age', '86400')
        return request.response
    else:
        return HTTPForbidden()
