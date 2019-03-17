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

import argparse
import logging
import os
import pkg_resources
import jinja2
from cryptography.fernet import Fernet


log = logging.getLogger(__name__)


def gen_secret():
    return Fernet.generate_key().decode("utf8")


def main():
    parser = argparse.ArgumentParser(
        description="Generate AppEnlight static resources", add_help=False
    )
    parser.add_argument("config", help="Name of generated file")
    parser.add_argument(
        "--domain",
        default="appenlight-rhodecode.local",
        help="Domain which will be used to serve the application",
    )
    parser.add_argument(
        "--dbstring",
        default="postgresql://appenlight:test@127.0.0.1:5432/appenlight",
        help="Domain which will be used to serve the application",
    )
    args = parser.parse_args()
    ini_path = os.path.join("templates", "ini", "production.ini.jinja2")
    template_str = pkg_resources.resource_string("appenlight", ini_path)
    template = jinja2.Template(template_str.decode("utf8"))
    template_vars = {
        "appenlight_encryption_secret": gen_secret(),
        "appenlight_authtkt_secret": gen_secret(),
        "appenlight_redis_session_secret": gen_secret(),
        "appenlight_domain": args.domain,
        "appenlight_dbstring": args.dbstring,
    }
    compiled = template.render(**template_vars)
    with open(args.config, "w") as f:
        f.write(compiled)
