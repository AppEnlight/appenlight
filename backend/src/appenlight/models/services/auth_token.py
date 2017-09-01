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
