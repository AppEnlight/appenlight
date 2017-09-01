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

import argparse
import getpass
import logging

from pyramid.paster import setup_logging, bootstrap
from pyramid.threadlocal import get_current_request

from appenlight.forms import UserRegisterForm
from appenlight.lib.ext_json import json
from appenlight.models import (
    DBSession,
    Group,
    GroupPermission,
    User,
    AuthToken
)
from appenlight.models.services.group import GroupService

log = logging.getLogger(__name__)

_ = str


def is_yes(input_data):
    return input_data in ['y', 'yes']


def is_no(input_data):
    return input_data in ['n', 'no']


def main():
    parser = argparse.ArgumentParser(
        description='Populate AppEnlight database',
        add_help=False)
    parser.add_argument('-c', '--config', required=True,
                        help='Configuration ini file of application')
    parser.add_argument('--username', default=None,
                        help='User  to create')
    parser.add_argument('--password', default=None,
                        help='Password for created user')
    parser.add_argument('--email', default=None,
                        help='Email for created user')
    parser.add_argument('--auth-token', default=None,
                        help='Auth token for created user')
    args = parser.parse_args()
    config_uri = args.config

    setup_logging(config_uri)
    env = bootstrap(config_uri)
    request = env['request']
    with get_current_request().tm:
        group = GroupService.by_id(1)
        if not group:
            group = Group(id=1, group_name='Administrators',
                           description="Top level permission owners")
            DBSession.add(group)
            permission = GroupPermission(perm_name='root_administration')
            group.permissions.append(permission)

    create_user = True if args.username else None
    while create_user is None:
        response = input(
            'Do you want to create a new admin? (n)\n').lower()

        if is_yes(response or 'n'):
            create_user = True
        elif is_no(response or 'n'):
            create_user = False

    if create_user:
        csrf_token = request.session.get_csrf_token()
        user_name = args.username
        print('*********************************************************')
        while user_name is None:
            response = input('What is the username of new admin?\n')
            form = UserRegisterForm(
                user_name=response, csrf_token=csrf_token,
                csrf_context=request)
            form.validate()
            if form.user_name.errors:
                print(form.user_name.errors[0])
            else:
                user_name = response
                print('The admin username is "{}"\n'.format(user_name))
        print('*********************************************************')
        email = args.email
        while email is None:
            response = input('What is the email of admin account?\n')
            form = UserRegisterForm(
                email=response, csrf_token=csrf_token,
                csrf_context=request)
            form.validate()
            if form.email.errors:
                print(form.email.errors[0])
            else:
                email = response
                print('The admin email is "{}"\n'.format(email))
        print('*********************************************************')
        user_password = args.password
        confirmed_password = args.password
        while user_password is None or confirmed_password is None:
            response = getpass.getpass(
                'What is the password for admin account?\n')
            form = UserRegisterForm(
                user_password=response, csrf_token=csrf_token,
                csrf_context=request)
            form.validate()
            if form.user_password.errors:
                print(form.user_password.errors[0])
            else:
                user_password = response

            response = getpass.getpass('Please confirm the password.\n')
            if user_password == response:
                confirmed_password = response
            else:
                print('Passwords do not match. Please try again')
        print('*********************************************************')

    with get_current_request().tm:
        if create_user:
            group = GroupService.by_id(1)
            user = User(user_name=user_name, email=email, status=1)
            user.regenerate_security_code()
            user.set_password(user_password)
            DBSession.add(user)
            token = AuthToken(description="Uptime monitoring token")
            if args.auth_token:
                token.token = args.auth_token
            user.auth_tokens.append(token)
            group.users.append(user)
            print('USER CREATED')
            print(json.dumps(user.get_dict()))
            print('*********************************************************')
            print('AUTH TOKEN')
            print(json.dumps(user.auth_tokens[0].get_dict()))
