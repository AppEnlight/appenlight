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

import logging
import sqlalchemy as sa

from datetime import datetime
from appenlight.models import Base
from ziggurat_foundations.models.base import BaseModel
from ziggurat_foundations.models.services.user import UserService

log = logging.getLogger(__name__)


class AuthToken(Base, BaseModel):
    """
    Stores information about possible alerting options
    """

    __tablename__ = "auth_tokens"

    id = sa.Column(sa.Integer, primary_key=True, nullable=False)
    token = sa.Column(
        sa.Unicode(40),
        nullable=False,
        default=lambda x: UserService.generate_random_string(40),
    )
    owner_id = sa.Column(
        sa.Unicode(30),
        sa.ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"),
    )
    creation_date = sa.Column(sa.DateTime, default=lambda x: datetime.utcnow())
    expires = sa.Column(sa.DateTime)
    description = sa.Column(sa.Unicode, default="")

    @property
    def is_expired(self):
        if self.expires:
            return self.expires < datetime.utcnow()
        else:
            return False

    def __str__(self):
        return "<AuthToken u:%s t:%s...>" % (self.owner_id, self.token[0:10])
