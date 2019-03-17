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

import re
from appenlight.lib.ext_json import json
from jinja2 import Markup, escape, evalcontextfilter

_paragraph_re = re.compile(r"(?:\r\n|\r|\n){2,}")


@evalcontextfilter
def nl2br(eval_ctx, value):
    if eval_ctx.autoescape:
        result = "\n\n".join(
            "<p>%s</p>" % p.replace("\n", Markup("<br>\n"))
            for p in _paragraph_re.split(escape(value))
        )
    else:
        result = "\n\n".join(
            "<p>%s</p>" % p.replace("\n", "<br>\n")
            for p in _paragraph_re.split(escape(value))
        )
    if eval_ctx.autoescape:
        result = Markup(result)
    return result


@evalcontextfilter
def toJSONUnsafe(eval_ctx, value):
    encoded = (
        json.dumps(value)
        .replace("&", "\\u0026")
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace(">", "\\u003e")
        .replace('"', "\\u0022")
        .replace("'", "\\u0027")
        .replace(r"\n", "/\\\n")
    )
    return Markup("'%s'" % encoded)
