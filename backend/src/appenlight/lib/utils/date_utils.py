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

from datetime import tzinfo, timedelta, datetime
from dateutil.relativedelta import relativedelta
import logging

log = logging.getLogger(__name__)


def to_relativedelta(time_delta):
    return relativedelta(
        seconds=int(time_delta.total_seconds()), microseconds=time_delta.microseconds
    )


def convert_date(date_str, return_utcnow_if_wrong=True, normalize_future=False):
    utcnow = datetime.utcnow()
    if isinstance(date_str, datetime):
        # get rid of tzinfo
        return date_str.replace(tzinfo=None)
    if not date_str and return_utcnow_if_wrong:
        return utcnow
    try:
        try:
            if "Z" in date_str:
                date_str = date_str[: date_str.index("Z")]
            if "." in date_str:
                date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f")
            else:
                date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
        except Exception:
            # bw compat with old client
            date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S,%f")
    except Exception:
        if return_utcnow_if_wrong:
            date = utcnow
        else:
            date = None
    if normalize_future and date and date > (utcnow + timedelta(minutes=3)):
        log.warning("time %s in future + 3 min, normalizing" % date)
        return utcnow
    return date
