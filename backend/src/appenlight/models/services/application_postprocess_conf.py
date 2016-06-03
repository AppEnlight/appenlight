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


from appenlight.models import get_db_session
from appenlight.models.application_postprocess_conf import ApplicationPostprocessConf
from appenlight.models.services.base import BaseService


class ApplicationPostprocessConfService(BaseService):

    @classmethod
    def by_pkey(cls, pkey, db_session=None):
        db_session = get_db_session(db_session)
        query = db_session.query(ApplicationPostprocessConf)
        return query.filter(ApplicationPostprocessConf.pkey == pkey).first()

    @classmethod
    def by_pkey_and_resource_id(cls, pkey, resource_id, db_session=None):
        db_session = get_db_session(db_session)
        query = db_session.query(ApplicationPostprocessConf)
        query = query.filter(ApplicationPostprocessConf.resource_id == resource_id)
        return query.filter(ApplicationPostprocessConf.pkey == pkey).first()
