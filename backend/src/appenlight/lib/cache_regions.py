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

import copy
import hashlib
import inspect

from dogpile.cache import make_region
from dogpile.cache.util import compat

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
