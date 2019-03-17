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

import json
from datetime import datetime, date, timedelta

DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return {"__type__": "__datetime__", "iso": obj.strftime(DATE_FORMAT)}
        elif isinstance(obj, date):
            return {"__type__": "__date__", "iso": obj.strftime(DATE_FORMAT)}
        elif isinstance(obj, timedelta):
            return {"__type__": "__timedelta__", "seconds": obj.total_seconds()}
        else:
            return json.JSONEncoder.default(self, obj)


def date_decoder(dct):
    if "__type__" in dct:
        if dct["__type__"] == "__datetime__":
            return datetime.strptime(dct["iso"], DATE_FORMAT)
        elif dct["__type__"] == "__date__":
            return datetime.strptime(dct["iso"], DATE_FORMAT).date()
        elif dct["__type__"] == "__timedelta__":
            return timedelta(seconds=dct["seconds"])
    return dct


def json_dumps(obj):
    return json.dumps(obj, cls=DateEncoder)


def json_loads(obj):
    return json.loads(obj.decode("utf8"), object_hook=date_decoder)
