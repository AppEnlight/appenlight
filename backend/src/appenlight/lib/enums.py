import collections
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
