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

import sqlalchemy as sa
import hashlib

from datetime import datetime, timedelta
from appenlight.models import Base
from sqlalchemy.dialects.postgresql import JSON
from ziggurat_foundations.models.base import BaseModel


class SlowCall(Base, BaseModel):
    __tablename__ = "slow_calls"
    __table_args__ = {"implicit_returning": False}

    resource_id = sa.Column(sa.Integer(), nullable=False, index=True)
    id = sa.Column(sa.Integer, nullable=False, primary_key=True)
    report_id = sa.Column(
        sa.BigInteger,
        sa.ForeignKey("reports.id", ondelete="cascade", onupdate="cascade"),
        primary_key=True,
    )
    duration = sa.Column(sa.Float(), default=0)
    statement = sa.Column(sa.UnicodeText(), default="")
    statement_hash = sa.Column(sa.Unicode(60), default="")
    parameters = sa.Column(JSON(), nullable=False, default=dict)
    type = sa.Column(sa.Unicode(16), default="")
    subtype = sa.Column(sa.Unicode(16), default=None)
    location = sa.Column(sa.Unicode(255), default="")
    timestamp = sa.Column(
        sa.DateTime(), default=datetime.utcnow, server_default=sa.func.now()
    )
    report_group_time = sa.Column(
        sa.DateTime(), default=datetime.utcnow, server_default=sa.func.now()
    )

    def set_data(
        self, data, protocol_version=None, resource_id=None, report_group=None
    ):
        self.resource_id = resource_id
        if data.get("start") and data.get("end"):
            self.timestamp = data.get("start")
            d = data.get("end") - data.get("start")
            self.duration = d.total_seconds()
        self.statement = data.get("statement", "")
        self.type = data.get("type", "unknown")[:16]
        self.parameters = data.get("parameters", {})
        self.location = data.get("location", "")[:255]
        self.report_group_time = report_group.first_timestamp
        if "subtype" in data:
            self.subtype = data.get("subtype", "unknown")[:16]
        if self.type == "tmpl":
            self.set_hash("{} {}".format(self.statement, self.parameters))
        else:
            self.set_hash()

    def set_hash(self, custom_statement=None):
        statement = custom_statement or self.statement
        self.statement_hash = hashlib.sha1(statement.encode("utf8")).hexdigest()

    @property
    def end_time(self):
        if self.duration and self.timestamp:
            return self.timestamp + timedelta(seconds=self.duration)
        return None

    def get_dict(self):
        instance_dict = super(SlowCall, self).get_dict()
        instance_dict["children"] = []
        instance_dict["end_time"] = self.end_time
        return instance_dict

    def es_doc(self):
        doc = {
            "resource_id": self.resource_id,
            "timestamp": self.timestamp,
            "slow_call_id": str(self.id),
            "permanent": False,
            "request_id": None,
            "log_level": "UNKNOWN",
            "message": self.statement,
            "namespace": "appenlight.slow_call",
            "tags": {
                "report_id": {
                    "values": self.report_id,
                    "numeric_values": self.report_id,
                },
                "duration": {"values": None, "numeric_values": self.duration},
                "statement_hash": {
                    "values": self.statement_hash,
                    "numeric_values": None,
                },
                "type": {"values": self.type, "numeric_values": None},
                "subtype": {"values": self.subtype, "numeric_values": None},
                "location": {"values": self.location, "numeric_values": None},
                "parameters": {"values": None, "numeric_values": None},
            },
            "tag_list": [
                "report_id",
                "duration",
                "statement_hash",
                "type",
                "subtype",
                "location",
            ],
        }
        if isinstance(self.parameters, str):
            doc["tags"]["parameters"]["values"] = self.parameters[:255]
        return doc

    @property
    def partition_id(self):
        return "rcae_sc_%s" % self.report_group_time.strftime("%Y_%m")
