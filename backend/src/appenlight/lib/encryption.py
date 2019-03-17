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

# this gets set on runtime
from cryptography.fernet import Fernet

ENCRYPTION_SECRET = None


def encrypt_fernet(value):
    # avoid double encryption
    # not sure if this is needed but it won't hurt too much to have this
    if value.startswith("enc$fernet$"):
        return value
    f = Fernet(ENCRYPTION_SECRET)
    return "enc$fernet${}".format(f.encrypt(value.encode("utf8")).decode("utf8"))


def decrypt_fernet(value):
    parts = value.split("$", 3)
    if not len(parts) == 3:
        # not encrypted values
        return value
    else:
        f = Fernet(ENCRYPTION_SECRET)
        decrypted_data = f.decrypt(parts[2].encode("utf8")).decode("utf8")
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
