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
from sqlalchemy.ext.declarative import declared_attr
from ziggurat_foundations.models.external_identity import ExternalIdentityMixin

from appenlight.models import Base
from appenlight.lib.sqlalchemy_fields import EncryptedUnicode


class ExternalIdentity(ExternalIdentityMixin, Base):
    @declared_attr
    def access_token(self):
        return sa.Column(EncryptedUnicode(255), default='')

    @declared_attr
    def alt_token(self):
        return sa.Column(EncryptedUnicode(255), default='')

    @declared_attr
    def token_secret(self):
        return sa.Column(EncryptedUnicode(255), default='')
