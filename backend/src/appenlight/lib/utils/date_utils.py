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

from datetime import tzinfo, timedelta, datetime
from dateutil.relativedelta import relativedelta
import logging

log = logging.getLogger(__name__)


def to_relativedelta(time_delta):
    return relativedelta(seconds=int(time_delta.total_seconds()),
                         microseconds=time_delta.microseconds)


def convert_date(date_str, return_utcnow_if_wrong=True,
                 normalize_future=False):
    utcnow = datetime.utcnow()
    if isinstance(date_str, datetime):
        # get rid of tzinfo
        return date_str.replace(tzinfo=None)
    if not date_str and return_utcnow_if_wrong:
        return utcnow
    try:
        try:
            if 'Z' in date_str:
                date_str = date_str[:date_str.index('Z')]
            if '.' in date_str:
                date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%f')
            else:
                date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S')
        except Exception:
            # bw compat with old client
            date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S,%f')
    except Exception:
        if return_utcnow_if_wrong:
            date = utcnow
        else:
            date = None
    if normalize_future and date and date > (utcnow + timedelta(minutes=3)):
        log.warning('time %s in future + 3 min, normalizing' % date)
        return utcnow
    return date
