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
# AppEnlight Enterprise Edition, including its added features, Support
# services, and proprietary license terms, please see
# https://rhodecode.com/licenses/

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
    __tablename__ = 'auth_tokens'

    id = sa.Column(sa.Integer, primary_key=True, nullable=False)
    token = sa.Column(sa.Unicode(40), nullable=False,
                      default=lambda x: UserService.generate_random_string(40))
    owner_id = sa.Column(sa.Unicode(30),
                         sa.ForeignKey('users.id', onupdate='CASCADE',
                                       ondelete='CASCADE'))
    creation_date = sa.Column(sa.DateTime, default=lambda x: datetime.utcnow())
    expires = sa.Column(sa.DateTime)
    description = sa.Column(sa.Unicode, default='')

    @property
    def is_expired(self):
        if self.expires:
            return self.expires < datetime.utcnow()
        else:
            return False

    def __str__(self):
        return '<AuthToken u:%s t:%s...>' % (self.owner_id, self.token[0:10])
