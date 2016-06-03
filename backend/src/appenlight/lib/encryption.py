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

# this gets set on runtime
from cryptography.fernet import Fernet

ENCRYPTION_SECRET = None


def encrypt_fernet(value):
    # avoid double encryption
    # not sure if this is needed but it won't hurt too much to have this
    if value.startswith('enc$fernet$'):
        return value
    f = Fernet(ENCRYPTION_SECRET)
    return 'enc$fernet${}'.format(f.encrypt(value.encode('utf8')).decode('utf8'))


def decrypt_fernet(value):
    parts = value.split('$', 3)
    if not len(parts) == 3:
        # not encrypted values
        return value
    else:
        f = Fernet(ENCRYPTION_SECRET)
        decrypted_data = f.decrypt(parts[2].encode('utf8')).decode('utf8')
        return decrypted_data


def encrypt_dictionary_keys(_dict, exclude_keys=None):
    if not exclude_keys:
        exclude_keys = []
    keys = [k for k in _dict.keys() if k not in exclude_keys]
    for k in keys:
        _dict[k] = encrypt_fernet(_dict[k])
    return _dict


def decrypt_dictionary_keys(_dict, exclude_keys=None):
    if not exclude_keys:
        exclude_keys = []
    keys = [k for k in _dict.keys() if k not in exclude_keys]
    for k in keys:
        _dict[k] = decrypt_fernet(_dict[k])
    return _dict
