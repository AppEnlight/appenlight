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
import shutil

from pyramid.paster import setup_logging
from pyramid.paster import bootstrap

log = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="Generate AppEnlight static resources", add_help=False
    )
    parser.add_argument(
        "-c", "--config", required=True, help="Configuration ini file of application"
    )
    args = parser.parse_args()
    config_uri = args.config
    setup_logging(config_uri)
    env = bootstrap(config_uri)
    registry = env["registry"]
    settings = registry.settings
    if os.path.exists(settings["webassets.dir"]):
        shutil.rmtree(settings["webassets.dir"])
    os.mkdir(settings["webassets.dir"])
    ae_basedir = pkg_resources.resource_filename("appenlight", "static")
    shutil.copytree(ae_basedir, os.path.join(settings["webassets.dir"], "appenlight"))

    for plugin_name, config in registry.appenlight_plugins.items():
        if config["static"]:
            shutil.copytree(
                config["static"], os.path.join(settings["webassets.dir"], plugin_name)
            )

    for root, dirs, files in os.walk(settings["webassets.dir"]):
        for item in dirs:
            os.chmod(os.path.join(root, item), 0o775)
        for item in files:
            os.chmod(os.path.join(root, item), 0o664)
