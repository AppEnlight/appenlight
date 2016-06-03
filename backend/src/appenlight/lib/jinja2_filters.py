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

import re
from appenlight.lib.ext_json import json
from jinja2 import Markup, escape, evalcontextfilter

_paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')


@evalcontextfilter
def nl2br(eval_ctx, value):
    if eval_ctx.autoescape:
        result = '\n\n'.join('<p>%s</p>' % p.replace('\n', Markup('<br>\n'))
                              for p in _paragraph_re.split(escape(value)))
    else:
        result = '\n\n'.join('<p>%s</p>' % p.replace('\n', '<br>\n')
                              for p in _paragraph_re.split(escape(value)))
    if eval_ctx.autoescape:
        result = Markup(result)
    return result


@evalcontextfilter
def toJSONUnsafe(eval_ctx, value):
    encoded = json.dumps(value).replace('&', '\\u0026') \
        .replace('<', '\\u003c') \
        .replace('>', '\\u003e') \
        .replace('>', '\\u003e') \
        .replace('"', '\\u0022') \
        .replace("'", '\\u0027') \
        .replace(r'\n', '/\\\n')
    return Markup("'%s'" % encoded)
