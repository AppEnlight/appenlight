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

from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON

from ziggurat_foundations.models.base import BaseModel
from appenlight.lib.utils import convert_es_type
from appenlight.models import Base


class Metric(Base, BaseModel):
    __tablename__ = "metrics"
    __table_args__ = {"implicit_returning": False}

    pkey = sa.Column(sa.BigInteger(), primary_key=True)
    resource_id = sa.Column(
        sa.Integer(),
        sa.ForeignKey("applications.resource_id"),
        nullable=False,
        primary_key=True,
    )
    timestamp = sa.Column(
        sa.DateTime(), default=datetime.utcnow, server_default=sa.func.now()
    )
    tags = sa.Column(JSON(), default={})
    namespace = sa.Column(sa.Unicode(255))

    @property
    def partition_id(self):
        return "rcae_m_%s" % self.timestamp.strftime("%Y_%m_%d")

    def es_doc(self):
        tags = {}
        tag_list = []
        for name, value in self.tags.items():
            # replace dot in indexed tag name
            name = name.replace(".", "_")
            tag_list.append(name)
            tags[name] = {
                "values": convert_es_type(value),
                "numeric_values": value
                if (isinstance(value, (int, float)) and not isinstance(value, bool))
                else None,
            }

        return {
            "metric_id": self.pkey,
            "resource_id": self.resource_id,
            "timestamp": self.timestamp,
            "namespace": self.namespace,
            "tags": tags,
            "tag_list": tag_list,
        }
