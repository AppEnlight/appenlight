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

import logging

from appenlight.models.auth_token import AuthToken
from appenlight.models.services.base import BaseService
from ziggurat_foundations.models.base import get_db_session

log = logging.getLogger(__name__)


class AuthTokenService(BaseService):
    @classmethod
    def by_token(cls, token, db_session=None):
        db_session = get_db_session(db_session)
        query = db_session.query(AuthToken).filter(AuthToken.token == token)
        return query.first()
