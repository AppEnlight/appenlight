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
    current_count = Datastores.redis.incr(key, to_increment)
    Datastores.redis.expire(key, 3600 * 24)
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
