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

import sqlalchemy as sa
from ziggurat_foundations.models.base import BaseModel
from sqlalchemy.dialects.postgres import JSON

from . import Base


class PluginConfig(Base, BaseModel):
    __tablename__ = 'plugin_configs'

    id = sa.Column(sa.Integer, primary_key=True)
    plugin_name = sa.Column(sa.Unicode)
    section = sa.Column(sa.Unicode)
    config = sa.Column(JSON, nullable=False)
    resource_id = sa.Column(sa.Integer(),
                            sa.ForeignKey('resources.resource_id',
                                          onupdate='cascade',
                                          ondelete='cascade'))
    owner_id = sa.Column(sa.Integer(),
                         sa.ForeignKey('users.id', onupdate='cascade',
                                       ondelete='cascade'))

    def __json__(self, request):
        return self.get_dict()
