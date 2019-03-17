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
from datetime import datetime
from ziggurat_foundations.models.base import BaseModel
from sqlalchemy.dialects.postgresql import JSON

from . import Base


class Tag(Base, BaseModel):
    __tablename__ = 'tags'

    id = sa.Column(sa.Integer, primary_key=True)
    resource_id = sa.Column(sa.Integer,
                            sa.ForeignKey('resources.resource_id'))
    name = sa.Column(sa.Unicode(512), nullable=False)
    value = sa.Column(JSON, nullable=False)
    first_timestamp = sa.Column(sa.DateTime(), default=datetime.utcnow,
                                server_default=sa.func.now())
    last_timestamp = sa.Column(sa.DateTime(), default=datetime.utcnow,
                               server_default=sa.func.now())
    times_seen = sa.Column(sa.Integer, nullable=False, default=0)
