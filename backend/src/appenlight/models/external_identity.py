# -*- coding: utf-8 -*-

# Copyright (C) 2010-2016  RhodeCode GmbH
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License, version 3
# (only), as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# This program is dual-licensed. If you wish to learn more about the
# App Enlight Enterprise Edition, including its added features, Support
# services, and proprietary license terms, please see
# https://rhodecode.com/licenses/

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
