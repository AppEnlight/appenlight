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

import binascii
import sqlalchemy.types as types

import appenlight.lib.encryption as encryption


class BinaryHex(types.TypeDecorator):
    impl = types.LargeBinary

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = binascii.unhexlify(value)

        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = binascii.hexlify(value)
        return value


class EncryptedUnicode(types.TypeDecorator):
    impl = types.Unicode

    def process_bind_param(self, value, dialect):
        if not value:
            return value
        return encryption.encrypt_fernet(value)

    def process_result_value(self, value, dialect):
        if not value:
            return value
        return encryption.decrypt_fernet(value)
