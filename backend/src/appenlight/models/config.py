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
from ziggurat_foundations.models.base import BaseModel
from sqlalchemy.dialects.postgresql import JSON

from . import Base


class Config(Base, BaseModel):
    __tablename__ = 'config'

    key = sa.Column(sa.Unicode, primary_key=True)
    section = sa.Column(sa.Unicode, primary_key=True)
    value = sa.Column(JSON, nullable=False)

    def __json__(self, request):
        return self.get_dict()
