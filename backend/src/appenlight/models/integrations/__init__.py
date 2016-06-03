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
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.hybrid import hybrid_property
from ziggurat_foundations.models.base import BaseModel

from appenlight.lib.encryption import decrypt_dictionary_keys
from appenlight.lib.encryption import encrypt_dictionary_keys
from appenlight.models import Base, get_db_session


class IntegrationException(Exception):
    pass


class IntegrationBase(Base, BaseModel):
    """
    Model from which all integrations inherit using polymorphic approach
    """
    __tablename__ = 'integrations'

    front_visible = False
    as_alert_channel = False
    supports_report_alerting = False

    id = sa.Column(sa.Integer, primary_key=True)
    resource_id = sa.Column(sa.Integer,
                            sa.ForeignKey('applications.resource_id'))
    integration_name = sa.Column(sa.Unicode(64))
    _config = sa.Column('config', JSON(), nullable=False, default='')
    modified_date = sa.Column(sa.DateTime)

    channel = sa.orm.relationship('AlertChannel',
                                  cascade="all,delete-orphan",
                                  passive_deletes=True,
                                  passive_updates=True,
                                  uselist=False,
                                  backref='integration')

    __mapper_args__ = {
        'polymorphic_on': 'integration_name',
        'polymorphic_identity': 'integration'
    }

    @classmethod
    def by_app_id_and_integration_name(cls, resource_id, integration_name,
                                       db_session=None):
        db_session = get_db_session(db_session)
        query = db_session.query(cls)
        query = query.filter(cls.integration_name == integration_name)
        query = query.filter(cls.resource_id == resource_id)
        return query.first()

    @hybrid_property
    def config(self):
        return decrypt_dictionary_keys(self._config)

    @config.setter
    def config(self, value):
        if not hasattr(value, 'items'):
            raise Exception('IntegrationBase.config only accepts '
                            'flat dictionaries')
        self._config = encrypt_dictionary_keys(value)
