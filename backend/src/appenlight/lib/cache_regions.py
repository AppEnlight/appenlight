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

import copy
import hashlib
import inspect

from dogpile.cache import make_region, compat

regions = None


def key_mangler(key):
    return "appenlight:dogpile:{}".format(key)


def hashgen(namespace, fn, to_str=compat.string_type):
    """Return a function that generates a string
    key, based on a given function as well as
    arguments to the returned function itself.

    This is used by :meth:`.CacheRegion.cache_on_arguments`
    to generate a cache key from a decorated function.

    It can be replaced using the ``function_key_generator``
    argument passed to :func:`.make_region`.

    """

    if namespace is None:
        namespace = '%s:%s' % (fn.__module__, fn.__name__)
    else:
        namespace = '%s:%s|%s' % (fn.__module__, fn.__name__, namespace)

    args = inspect.getargspec(fn)
    has_self = args[0] and args[0][0] in ('self', 'cls')

    def generate_key(*args, **kw):
        if kw:
            raise ValueError(
                "dogpile.cache's default key creation "
                "function does not accept keyword arguments.")
        if has_self:
            args = args[1:]

        return namespace + "|" + hashlib.sha1(
            " ".join(map(to_str, args)).encode('utf8')).hexdigest()

    return generate_key


class CacheRegions(object):
    def __init__(self, settings):
        config_redis = {"arguments": settings}

        self.redis_min_1 = make_region(
            function_key_generator=hashgen,
            key_mangler=key_mangler).configure(
            "dogpile.cache.redis",
            expiration_time=60,
            **copy.deepcopy(config_redis))
        self.redis_min_5 = make_region(
            function_key_generator=hashgen,
            key_mangler=key_mangler).configure(
            "dogpile.cache.redis",
            expiration_time=300,
            **copy.deepcopy(config_redis))

        self.redis_min_10 = make_region(
            function_key_generator=hashgen,
            key_mangler=key_mangler).configure(
            "dogpile.cache.redis",
            expiration_time=60,
            **copy.deepcopy(config_redis))

        self.redis_min_60 = make_region(
            function_key_generator=hashgen,
            key_mangler=key_mangler).configure(
            "dogpile.cache.redis",
            expiration_time=3600,
            **copy.deepcopy(config_redis))

        self.redis_sec_1 = make_region(
            function_key_generator=hashgen,
            key_mangler=key_mangler).configure(
            "dogpile.cache.redis",
            expiration_time=1,
            **copy.deepcopy(config_redis))

        self.redis_sec_5 = make_region(
            function_key_generator=hashgen,
            key_mangler=key_mangler).configure(
            "dogpile.cache.redis",
            expiration_time=5,
            **copy.deepcopy(config_redis))

        self.redis_sec_30 = make_region(
            function_key_generator=hashgen,
            key_mangler=key_mangler).configure(
            "dogpile.cache.redis",
            expiration_time=30,
            **copy.deepcopy(config_redis))

        self.redis_day_1 = make_region(
            function_key_generator=hashgen,
            key_mangler=key_mangler).configure(
            "dogpile.cache.redis",
            expiration_time=86400,
            **copy.deepcopy(config_redis))

        self.redis_day_7 = make_region(
            function_key_generator=hashgen,
            key_mangler=key_mangler).configure(
            "dogpile.cache.redis",
            expiration_time=86400 * 7,
            **copy.deepcopy(config_redis))

        self.redis_day_30 = make_region(
            function_key_generator=hashgen,
            key_mangler=key_mangler).configure(
            "dogpile.cache.redis",
            expiration_time=86400 * 30,
            **copy.deepcopy(config_redis))

        self.memory_day_1 = make_region(
            function_key_generator=hashgen,
            key_mangler=key_mangler).configure(
            "dogpile.cache.memory",
            expiration_time=86400,
            **copy.deepcopy(config_redis))

        self.memory_sec_1 = make_region(
            function_key_generator=hashgen,
            key_mangler=key_mangler).configure(
            "dogpile.cache.memory",
            expiration_time=1)

        self.memory_sec_5 = make_region(
            function_key_generator=hashgen,
            key_mangler=key_mangler).configure(
            "dogpile.cache.memory",
            expiration_time=5)

        self.memory_min_1 = make_region(
            function_key_generator=hashgen,
            key_mangler=key_mangler).configure(
            "dogpile.cache.memory",
            expiration_time=60)

        self.memory_min_5 = make_region(
            function_key_generator=hashgen,
            key_mangler=key_mangler).configure(
            "dogpile.cache.memory",
            expiration_time=300)

        self.memory_min_10 = make_region(
            function_key_generator=hashgen,
            key_mangler=key_mangler).configure(
            "dogpile.cache.memory",
            expiration_time=600)

        self.memory_min_60 = make_region(
            function_key_generator=hashgen,
            key_mangler=key_mangler).configure(
            "dogpile.cache.memory",
            expiration_time=3600)


def get_region(region):
    return getattr(regions, region)
