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
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.hybrid import hybrid_property
from ziggurat_foundations.models.base import BaseModel

from appenlight.lib.encryption import decrypt_dictionary_keys
from appenlight.lib.encryption import encrypt_dictionary_keys
from appenlight.models import Base, get_db_session


class IntegrationException(Exception):
    pass


class IntegrationBase(Base, BaseModel):
    """
    Model from which all integrations inherit using polymorphic approach
    """

    __tablename__ = "integrations"

    front_visible = False
    as_alert_channel = False
    supports_report_alerting = False

    id = sa.Column(sa.Integer, primary_key=True)
    resource_id = sa.Column(sa.Integer, sa.ForeignKey("applications.resource_id"))
    integration_name = sa.Column(sa.Unicode(64))
    _config = sa.Column("config", JSON(), nullable=False, default="")
    modified_date = sa.Column(sa.DateTime)

    channel = sa.orm.relationship(
        "AlertChannel",
        cascade="all,delete-orphan",
        passive_deletes=True,
        passive_updates=True,
        uselist=False,
        backref="integration",
    )

    __mapper_args__ = {
        "polymorphic_on": "integration_name",
        "polymorphic_identity": "integration",
    }

    @classmethod
    def by_app_id_and_integration_name(
        cls, resource_id, integration_name, db_session=None
    ):
        db_session = get_db_session(db_session)
        query = db_session.query(cls)
        query = query.filter(cls.integration_name == integration_name)
        query = query.filter(cls.resource_id == resource_id)
        return query.first()

    @hybrid_property
    def config(self):
        return decrypt_dictionary_keys(self._config)

    @config.setter
    def config(self, value):
        if not hasattr(value, "items"):
            raise Exception("IntegrationBase.config only accepts " "flat dictionaries")
        self._config = encrypt_dictionary_keys(value)
