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

"""
Utility functions.
"""
import logging
import requests
import hashlib
import json
import copy
import uuid
import appenlight.lib.helpers as h
from collections import namedtuple
from datetime import timedelta, datetime, date
from dogpile.cache.api import NO_VALUE
from appenlight.models import Datastores
from appenlight.validators import (LogSearchSchema,
                                   TagListSchema,
                                   accepted_search_params)
from itsdangerous import TimestampSigner
from ziggurat_foundations.permissions import ALL_PERMISSIONS
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, MONTHLY, DAILY

log = logging.getLogger(__name__)


Stat = namedtuple('Stat', 'start_interval value')


def default_extractor(item):
    """
    :param item - item to extract date from
    """
    if hasattr(item, 'start_interval'):
        return item.start_interval
    return item['start_interval']


# fast gap generator
def gap_gen_default(start, step, itemiterator, end_time=None,
                    iv_extractor=None):
    """ generates a list of time/value items based on step and itemiterator
        if there are entries missing from iterator time/None will be returned
        instead
    :param start - datetime - what time should we start generating our values
    :param step - timedelta - stepsize
    :param itemiterator - iterable - we will check this iterable for values
    corresponding to generated steps
    :param end_time - datetime - when last step is >= end_time stop iterating
    :param iv_extractor - extracts current step from iterable items
    """

    if not iv_extractor:
        iv_extractor = default_extractor

    next_step = start
    minutes = step.total_seconds() / 60.0
    while next_step.minute % minutes != 0:
        next_step = next_step.replace(minute=next_step.minute - 1)
    for item in itemiterator:
        item_start_interval = iv_extractor(item)
        # do we have a match for current time step in our data?
        # no gen a new tuple with 0 values
        while next_step < item_start_interval:
            yield Stat(next_step, None)
            next_step = next_step + step
        if next_step == item_start_interval:
            yield Stat(item_start_interval, item)
            next_step = next_step + step
    if end_time:
        while next_step < end_time:
            yield Stat(next_step, None)
            next_step = next_step + step


class DateTimeEncoder(json.JSONEncoder):
    """ Simple datetime to ISO encoder for json serialization"""

    def default(self, obj):
        if isinstance(obj, date):
            return obj.isoformat()
        if isinstance(obj, datetime):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)


def cometd_request(secret, endpoint, payload, throw_exceptions=False,
                   servers=None):
    responses = []
    if not servers:
        servers = []

    signer = TimestampSigner(secret)
    sig_for_server = signer.sign(endpoint)
    for secret, server in [(s['secret'], s['server']) for s in servers]:
        response = {}
        secret_headers = {'x-channelstream-secret': sig_for_server,
                          'x-channelstream-endpoint': endpoint,
                          'Content-Type': 'application/json'}
        url = '%s%s' % (server, endpoint)
        try:
            response = requests.post(url,
                                     data=json.dumps(payload,
                                                     cls=DateTimeEncoder),
                                     headers=secret_headers,
                                     verify=False,
                                     timeout=2).json()
        except requests.exceptions.RequestException as e:
            if throw_exceptions:
                raise
        responses.append(response)
    return responses


def add_cors_headers(response):
    # allow CORS
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('XDomainRequestAllowed', '1')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    # response.headers.add('Access-Control-Allow-Credentials', 'true')
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type, Depth, User-Agent, X-File-Size, X-Requested-With, If-Modified-Since, X-File-Name, Cache-Control, Pragma, Origin, Connection, Referer, Cookie')
    response.headers.add('Access-Control-Max-Age', '86400')


from sqlalchemy.sql import compiler
from psycopg2.extensions import adapt as sqlescape


# or use the appropiate escape function from your db driver

def compile_query(query):
    dialect = query.session.bind.dialect
    statement = query.statement
    comp = compiler.SQLCompiler(dialect, statement)
    comp.compile()
    enc = dialect.encoding
    params = {}
    for k, v in comp.params.items():
        if isinstance(v, str):
            v = v.encode(enc)
        params[k] = sqlescape(v)
    return (comp.string.encode(enc) % params).decode(enc)


def convert_es_type(input_data):
    """
    This might need to convert some text or other types to corresponding ES types
    """
    return str(input_data)


ProtoVersion = namedtuple('ProtoVersion', ['major', 'minor', 'patch'])


def parse_proto(input_data):
    try:
        parts = [int(x) for x in input_data.split('.')]
        while len(parts) < 3:
            parts.append(0)
        return ProtoVersion(*parts)
    except Exception as e:
        log.info('Unknown protocol version: %s' % e)
    return ProtoVersion(99, 99, 99)


def es_index_name_limiter(start_date=None, end_date=None, months_in_past=6,
                          ixtypes=None):
    """
    This function limits the search to 6 months by default so we don't have to
    query 300 elasticsearch indices for 20 years of historical data for example
    """

    # should be cached later
    def get_possible_names():
        return list(Datastores.es.aliases().keys())

    possible_names = get_possible_names()
    es_index_types = []
    if not ixtypes:
        ixtypes = ['reports', 'metrics', 'logs']
    for t in ixtypes:
        if t == 'reports':
            es_index_types.append('rcae_r_%s')
        elif t == 'logs':
            es_index_types.append('rcae_l_%s')
        elif t == 'metrics':
            es_index_types.append('rcae_m_%s')
        elif t == 'uptime':
            es_index_types.append('rcae_u_%s')
        elif t == 'slow_calls':
            es_index_types.append('rcae_sc_%s')

    if start_date:
        start_date = copy.copy(start_date)
    else:
        if not end_date:
            end_date = datetime.utcnow()
        start_date = end_date + relativedelta(months=months_in_past * -1)

    if not end_date:
        end_date = start_date + relativedelta(months=months_in_past)

    index_dates = list(rrule(MONTHLY,
                             dtstart=start_date.date().replace(day=1),
                             until=end_date.date(),
                             count=36))
    index_names = []
    for ix_type in es_index_types:
        to_extend = [ix_type % d.strftime('%Y_%m') for d in index_dates
                     if ix_type % d.strftime('%Y_%m') in possible_names]
        index_names.extend(to_extend)
        for day in list(rrule(DAILY, dtstart=start_date.date(),
                              until=end_date.date(), count=366)):
            ix_name = ix_type % day.strftime('%Y_%m_%d')
            if ix_name in possible_names:
                index_names.append(ix_name)
    return index_names


def build_filter_settings_from_query_dict(
        request, params=None, override_app_ids=None,
        resource_permissions=None):
    """
    Builds list of normalized search terms for ES from query params
    ensuring application list is restricted to only applications user
    has access to

    :param params (dictionary)
    :param override_app_ids - list of application id's to use instead of
    applications user normally has access to
    """
    params = copy.deepcopy(params)
    applications = []
    if not resource_permissions:
        resource_permissions = ['view']

    if request.user:
        applications = request.user.resources_with_perms(
            resource_permissions, resource_types=['application'])

    # CRITICAL - this ensures our resultset is limited to only the ones
    # user has view permissions
    all_possible_app_ids = set([app.resource_id for app in applications])

    # if override is preset we force permission for app to be present
    # this allows users to see dashboards and applications they would
    # normally not be able to

    if override_app_ids:
        all_possible_app_ids = set(override_app_ids)

    schema = LogSearchSchema().bind(resources=all_possible_app_ids)
    tag_schema = TagListSchema()
    filter_settings = schema.deserialize(params)
    tag_list = []
    for k, v in list(filter_settings.items()):
        if k in accepted_search_params:
            continue
        tag_list.append({"name": k, "value": v, "op": 'eq'})
        # remove the key from filter_settings
        filter_settings.pop(k, None)
    tags = tag_schema.deserialize(tag_list)
    filter_settings['tags'] = tags
    return filter_settings


def gen_uuid():
    return str(uuid.uuid4())


def gen_uuid4_sha_hex():
    return hashlib.sha1(uuid.uuid4().bytes).hexdigest()


def permission_tuple_to_dict(data):
    out = {
        "user_name": None,
        "perm_name": data.perm_name,
        "owner": data.owner,
        "type": data.type,
        "resource_name": None,
        "resource_type": None,
        "resource_id": None,
        "group_name": None,
        "group_id": None
    }
    if data.user:
        out["user_name"] = data.user.user_name
    if data.perm_name == ALL_PERMISSIONS:
        out['perm_name'] = '__all_permissions__'
    if data.resource:
        out['resource_name'] = data.resource.resource_name
        out['resource_type'] = data.resource.resource_type
        out['resource_id'] = data.resource.resource_id
    if data.group:
        out['group_name'] = data.group.group_name
        out['group_id'] = data.group.id
    return out


def get_cached_buckets(request, stats_since, end_time, fn, cache_key,
                       gap_gen=None, db_session=None, step_interval=None,
                       iv_extractor=None,
                       rerange=False, *args, **kwargs):
    """ Takes "fn" that should return some data and tries to load the data
    dividing it into daily buckets - if the stats_since and end time give a
    delta bigger than 24hours, then only "todays" data is computed on the fly

    :param request: (request) request object
    :param stats_since: (datetime) start date of buckets range
    :param end_time: (datetime) end date of buckets range - utcnow() if None
    :param fn: (callable) callable to use to populate buckets should have
    following signature:
        def get_data(request, since_when, until, *args, **kwargs):

    :param cache_key: (string) cache key that will be used to build bucket
    caches
    :param gap_gen: (callable) gap generator - should return step intervals
    to use with out `fn` callable
    :param db_session: (Session) sqlalchemy session
    :param step_interval: (timedelta) optional step interval if we want to
    override the default determined from total start/end time delta
    :param iv_extractor: (callable) used to get step intervals from data
    returned by `fn` callable
    :param rerange: (bool) handy if we want to change ranges from hours to
    days when cached data is missing - will shorten execution time if `fn`
    callable supports that and we are working with multiple rows - like metrics
    :param args:
    :param kwargs:

    :return: iterable
    """
    if not end_time:
        end_time = datetime.utcnow().replace(second=0, microsecond=0)
    delta = end_time - stats_since
    # if smaller than 3 days we want to group by 5min else by 1h,
    # for 60 min group by min
    if not gap_gen:
        gap_gen = gap_gen_default
    if not iv_extractor:
        iv_extractor = default_extractor

    # do not use custom interval if total time range with new iv would exceed
    # end time
    if not step_interval or stats_since + step_interval >= end_time:
        if delta < h.time_deltas.get('12h')['delta']:
            step_interval = timedelta(seconds=60)
        elif delta < h.time_deltas.get('3d')['delta']:
            step_interval = timedelta(seconds=60 * 5)
        elif delta > h.time_deltas.get('2w')['delta']:
            step_interval = timedelta(days=1)
        else:
            step_interval = timedelta(minutes=60)

    if step_interval >= timedelta(minutes=60):
        log.info('cached_buckets:{}: adjusting start time '
                 'for hourly or daily intervals'.format(cache_key))
        stats_since = stats_since.replace(hour=0, minute=0)

    ranges = [i.start_interval for i in list(gap_gen(stats_since,
                                                     step_interval, [],
                                                     end_time=end_time))]
    buckets = {}
    storage_key = 'buckets:' + cache_key + '{}|{}'
    # this means we basicly cache per hour in 3-14 day intervals but i think
    # its fine at this point - will be faster than db access anyways

    if len(ranges) >= 1:
        last_ranges = [ranges[-1]]
    else:
        last_ranges = []
    if step_interval >= timedelta(minutes=60):
        for r in ranges:
            k = storage_key.format(step_interval.total_seconds(), r)
            value = request.registry.cache_regions.redis_day_30.get(k)
            # last buckets are never loaded from cache
            is_last_result = (
                r >= end_time - timedelta(hours=6) or r in last_ranges)
            if value is not NO_VALUE and not is_last_result:
                log.info("cached_buckets:{}: "
                         "loading range {} from cache".format(cache_key, r))
                buckets[r] = value
            else:
                log.info("cached_buckets:{}: "
                         "loading range {} from storage".format(cache_key, r))
                range_size = step_interval
                if (step_interval == timedelta(minutes=60) and
                        not is_last_result and rerange):
                    range_size = timedelta(days=1)
                    r = r.replace(hour=0, minute=0)
                    log.info("cached_buckets:{}: "
                             "loading collapsed "
                             "range {} {}".format(cache_key, r,
                                                  r + range_size))
                bucket_data = fn(
                    request, r, r + range_size, step_interval,
                    gap_gen, bucket_count=len(ranges), *args, **kwargs)
                for b in bucket_data:
                    b_iv = iv_extractor(b)
                    buckets[b_iv] = b
                    k2 = storage_key.format(
                        step_interval.total_seconds(), b_iv)
                    request.registry.cache_regions.redis_day_30.set(k2, b)
        log.info("cached_buckets:{}: saving cache".format(cache_key))
    else:
        # bucket count is 1 for short time ranges <= 24h from now
        bucket_data = fn(request, stats_since, end_time, step_interval,
                         gap_gen, bucket_count=1, *args, **kwargs)
        for b in bucket_data:
            buckets[iv_extractor(b)] = b
    return buckets


def get_cached_split_data(request, stats_since, end_time, fn, cache_key,
                          db_session=None, *args, **kwargs):
    """ Takes "fn" that should return some data and tries to load the data
    dividing it into 2 buckets - cached "since_from" bucket and "today"
    bucket - then the data can be reduced into single value

    Data is cached if the stats_since and end time give a delta bigger
    than 24hours - then only 24h is computed on the fly
    """
    if not end_time:
        end_time = datetime.utcnow().replace(second=0, microsecond=0)
    delta = end_time - stats_since

    if delta >= timedelta(minutes=60):
        log.info('cached_split_data:{}: adjusting start time '
                 'for hourly or daily intervals'.format(cache_key))
        stats_since = stats_since.replace(hour=0, minute=0)

    storage_key = 'buckets_split_data:' + cache_key + ':{}|{}'
    old_end_time = end_time.replace(hour=0, minute=0)

    final_storage_key = storage_key.format(delta.total_seconds(),
                                           old_end_time)
    older_data = None

    cdata = request.registry.cache_regions.redis_day_7.get(
        final_storage_key)

    if cdata:
        log.info("cached_split_data:{}: found old "
                 "bucket data".format(cache_key))
        older_data = cdata

    if (stats_since < end_time - h.time_deltas.get('24h')['delta'] and
            not cdata):
        log.info("cached_split_data:{}: didn't find the "
                 "start bucket in cache so load older data".format(cache_key))
        recent_stats_since = old_end_time
        older_data = fn(request, stats_since, recent_stats_since,
                        db_session=db_session, *args, **kwargs)
        request.registry.cache_regions.redis_day_7.set(final_storage_key,
                                                       older_data)
    elif stats_since < end_time - h.time_deltas.get('24h')['delta']:
        recent_stats_since = old_end_time
    else:
        recent_stats_since = stats_since

    log.info("cached_split_data:{}: loading fresh "
             "data bucksts from last 24h ".format(cache_key))
    todays_data = fn(request, recent_stats_since, end_time,
                     db_session=db_session, *args, **kwargs)
    return older_data, todays_data


def in_batches(seq, size):
    """
    Splits am iterable into batches of specified size
    :param seq (iterable)
    :param size integer
    """
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))
