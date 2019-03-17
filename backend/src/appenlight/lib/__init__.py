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

"""Miscellaneous support packages for {{project}}.
"""
import random
import string
import importlib

from appenlight_client.exceptions import get_current_traceback


def generate_random_string(chars=10):
    return "".join(random.sample(string.ascii_letters * 2 + string.digits, chars))


def to_integer_safe(input):
    try:
        return int(input)
    except (TypeError, ValueError):
        return None


def print_traceback(log):
    traceback = get_current_traceback(
        skip=1, show_hidden_frames=True, ignore_system_exceptions=True
    )
    exception_text = traceback.exception
    log.error(exception_text)
    log.error(traceback.plaintext)
    del traceback


def get_callable(import_string):
    import_module, indexer_callable = import_string.split(":")
    return getattr(importlib.import_module(import_module), indexer_callable)
