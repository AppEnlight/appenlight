import collections
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


class StupidEnum(object):
    @classmethod
    def set_inverse(cls):
        cls._inverse_values = dict(
            (y, x) for x, y in vars(cls).items() if
            not x.startswith('_') and not callable(y)
        )

    @classmethod
    def key_from_value(cls, value):
        if not hasattr(cls, '_inverse_values'):
            cls.set_inverse()
        return cls._inverse_values.get(value)


class ReportType(StupidEnum):
    unknown = 0
    error = 1
    not_found = 2
    slow = 3


class Language(StupidEnum):
    unknown = 0
    python = 1
    javascript = 2
    java = 3
    objectivec = 4
    swift = 5
    cpp = 6
    basic = 7
    csharp = 8
    php = 9
    perl = 10
    vb = 11
    vbnet = 12
    ruby = 13
    fsharp = 14
    actionscript = 15
    go = 16
    scala = 17
    haskell = 18
    erlang = 19
    haxe = 20
    scheme = 21


class LogLevel(StupidEnum):
    UNKNOWN = 0
    DEBUG = 2
    TRACE = 4
    INFO = 6
    WARNING = 8
    ERROR = 10
    CRITICAL = 12
    FATAL = 14


class LogLevelPython(StupidEnum):
    CRITICAL = 50
    ERROR = 40
    WARNING = 30
    INFO = 20
    DEBUG = 10
    NOTSET = 0


class ParsedSentryEventType(StupidEnum):
    ERROR_REPORT = 1
    LOG = 2
