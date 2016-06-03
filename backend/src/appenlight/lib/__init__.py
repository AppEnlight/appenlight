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

"""Miscellaneous support packages for {{project}}.
"""
import random
import string
import importlib

from appenlight_client.exceptions import get_current_traceback


def generate_random_string(chars=10):
    return ''.join(random.sample(string.ascii_letters * 2 + string.digits,
                                  chars))


def to_integer_safe(input):
    try:
        return int(input)
    except (TypeError, ValueError,):
        return None

def print_traceback(log):
    traceback = get_current_traceback(skip=1, show_hidden_frames=True,
                                      ignore_system_exceptions=True)
    exception_text = traceback.exception
    log.error(exception_text)
    log.error(traceback.plaintext)
    del traceback

def get_callable(import_string):
    import_module, indexer_callable = import_string.split(':')
    return getattr(importlib.import_module(import_module),
                   indexer_callable)
