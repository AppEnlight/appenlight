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

"""
Helper functions
"""
import copy
import datetime

from collections import namedtuple, OrderedDict

_ = lambda x: x

time_deltas = OrderedDict()

time_deltas["1m"] = {
    "delta": datetime.timedelta(minutes=1),
    "label": "1 minute",
    "minutes": 1,
}

time_deltas["5m"] = {
    "delta": datetime.timedelta(minutes=5),
    "label": "5 minutes",
    "minutes": 5,
}
time_deltas["30m"] = {
    "delta": datetime.timedelta(minutes=30),
    "label": "30 minutes",
    "minutes": 30,
}
time_deltas["1h"] = {
    "delta": datetime.timedelta(hours=1),
    "label": "60 minutes",
    "minutes": 60,
}
time_deltas["4h"] = {
    "delta": datetime.timedelta(hours=4),
    "label": "4 hours",
    "minutes": 60 * 4,
}
time_deltas["12h"] = {
    "delta": datetime.timedelta(hours=12),
    "label": "12 hours",
    "minutes": 60 * 12,
}
time_deltas["24h"] = {
    "delta": datetime.timedelta(hours=24),
    "label": "24 hours",
    "minutes": 60 * 24,
}
time_deltas["3d"] = {
    "delta": datetime.timedelta(days=3),
    "label": "3 days",
    "minutes": 60 * 24 * 3,
}
time_deltas["1w"] = {
    "delta": datetime.timedelta(days=7),
    "label": "7 days",
    "minutes": 60 * 24 * 7,
}
time_deltas["2w"] = {
    "delta": datetime.timedelta(days=14),
    "label": "14 days",
    "minutes": 60 * 24 * 14,
}
time_deltas["1M"] = {
    "delta": datetime.timedelta(days=31),
    "label": "31 days",
    "minutes": 60 * 24 * 31,
}
time_deltas["3M"] = {
    "delta": datetime.timedelta(days=31 * 3),
    "label": "3 months",
    "minutes": 60 * 24 * 31 * 3,
}
time_deltas["6M"] = {
    "delta": datetime.timedelta(days=31 * 6),
    "label": "6 months",
    "minutes": 60 * 24 * 31 * 6,
}
time_deltas["12M"] = {
    "delta": datetime.timedelta(days=31 * 12),
    "label": "12 months",
    "minutes": 60 * 24 * 31 * 12,
}

# used in json representation
time_options = dict(
    [
        (k, {"label": v["label"], "minutes": v["minutes"]})
        for k, v in time_deltas.items()
    ]
)
FlashMsg = namedtuple("FlashMsg", ["msg", "level"])


def get_flash(request):
    messages = []
    messages.extend(
        [FlashMsg(msg, "error") for msg in request.session.peek_flash("error")]
    )
    messages.extend(
        [FlashMsg(msg, "warning") for msg in request.session.peek_flash("warning")]
    )
    messages.extend([FlashMsg(msg, "notice") for msg in request.session.peek_flash()])
    return messages


def clear_flash(request):
    request.session.pop_flash("error")
    request.session.pop_flash("warning")
    request.session.pop_flash()


def get_type_formatted_flash(request):
    return [
        {"msg": message.msg, "type": message.level} for message in get_flash(request)
    ]


def gen_pagination_headers(request, paginator):
    headers = {
        "x-total-count": str(paginator.item_count),
        "x-current-page": str(paginator.page),
        "x-items-per-page": str(paginator.items_per_page),
    }
    params_dict = request.GET.dict_of_lists()
    last_page_params = copy.deepcopy(params_dict)
    last_page_params["page"] = paginator.last_page or 1
    first_page_params = copy.deepcopy(params_dict)
    first_page_params.pop("page", None)
    next_page_params = copy.deepcopy(params_dict)
    next_page_params["page"] = paginator.next_page or paginator.last_page or 1
    prev_page_params = copy.deepcopy(params_dict)
    prev_page_params["page"] = paginator.previous_page or 1
    lp_url = request.current_route_url(_query=last_page_params)
    fp_url = request.current_route_url(_query=first_page_params)
    links = ['rel="last", <{}>'.format(lp_url), 'rel="first", <{}>'.format(fp_url)]
    if first_page_params != prev_page_params:
        prev_url = request.current_route_url(_query=prev_page_params)
        links.append('rel="prev", <{}>'.format(prev_url))
    if last_page_params != next_page_params:
        next_url = request.current_route_url(_query=next_page_params)
        links.append('rel="next", <{}>'.format(next_url))
    headers["link"] = "; ".join(links)
    return headers
