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

import json
from datetime import datetime, date, timedelta

DATE_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return {
                '__type__': '__datetime__',
                'iso': obj.strftime(DATE_FORMAT)
            }
        elif isinstance(obj, date):
            return {
                '__type__': '__date__',
                'iso': obj.strftime(DATE_FORMAT)
            }
        elif isinstance(obj, timedelta):
            return {
                '__type__': '__timedelta__',
                'seconds': obj.total_seconds()
            }
        else:
            return json.JSONEncoder.default(self, obj)


def date_decoder(dct):
    if '__type__' in dct:
        if dct['__type__'] == '__datetime__':
            return datetime.strptime(dct['iso'], DATE_FORMAT)
        elif dct['__type__'] == '__date__':
            return datetime.strptime(dct['iso'], DATE_FORMAT).date()
        elif dct['__type__'] == '__timedelta__':
            return timedelta(seconds=dct['seconds'])
    return dct


def json_dumps(obj):
    return json.dumps(obj, cls=DateEncoder)


def json_loads(obj):
    return json.loads(obj.decode('utf8'), object_hook=date_decoder)
