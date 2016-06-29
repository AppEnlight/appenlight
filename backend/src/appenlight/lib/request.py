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

import json

from pyramid.security import unauthenticated_userid

import appenlight.lib.helpers as helpers

from authomatic.providers import oauth2, oauth1
from authomatic import Authomatic
from appenlight.models.user import User


class CSRFException(Exception):
    pass


class JSONException(Exception):
    pass


def get_csrf_token(request):
    return request.session.get_csrf_token()


def safe_json_body(request):
    """
    Returns None if json body is missing or erroneous
    """
    try:
        return request.json_body
    except ValueError:
        return None


def unsafe_json_body(request):
    """
    Throws JSONException if json can't deserialize
    """
    try:
        return request.json_body
    except ValueError:
        raise JSONException('Incorrect JSON')


def get_user(request):
    if not request.path_info.startswith('/static'):
        user_id = unauthenticated_userid(request)
        try:
            user_id = int(user_id)
        except Exception:
            return None

        if user_id:
            user = User.by_id(user_id)
            if user:
                request.environ['appenlight.username'] = '%d:%s' % (
                    user_id, user.user_name)
            return user
        else:
            return None


def es_conn(request):
    return request.registry.es_conn


def add_flash_to_headers(request, clear=True):
    """
    Adds pending flash messages to response, if clear is true clears out the
    flash queue
    """
    flash_msgs = helpers.get_type_formatted_flash(request)
    request.response.headers['x-flash-messages'] = json.dumps(flash_msgs)
    helpers.clear_flash(request)


def get_authomatic(request):
    settings = request.registry.settings
    # authomatic social auth
    authomatic_conf = {
        # callback http://yourapp.com/social_auth/twitter
        'twitter': {
            'class_': oauth1.Twitter,
            'consumer_key': settings.get('authomatic.pr.twitter.key', ''),
            'consumer_secret': settings.get('authomatic.pr.twitter.secret',
                                            ''),
        },
        # callback http://yourapp.com/social_auth/facebook
        'facebook': {
            'class_': oauth2.Facebook,
            'consumer_key': settings.get('authomatic.pr.facebook.app_id', ''),
            'consumer_secret': settings.get('authomatic.pr.facebook.secret',
                                            ''),
            'scope': ['email'],
        },
        # callback http://yourapp.com/social_auth/google
        'google': {
            'class_': oauth2.Google,
            'consumer_key': settings.get('authomatic.pr.google.key', ''),
            'consumer_secret': settings.get(
                'authomatic.pr.google.secret', ''),
            'scope': ['profile', 'email'],
        },
        'github': {
            'class_': oauth2.GitHub,
            'consumer_key': settings.get('authomatic.pr.github.key', ''),
            'consumer_secret': settings.get(
                'authomatic.pr.github.secret', ''),
            'scope': ['repo', 'public_repo', 'user:email'],
            'access_headers': {'User-Agent': 'AppEnlight'},
        },
        'bitbucket': {
            'class_': oauth1.Bitbucket,
            'consumer_key': settings.get('authomatic.pr.bitbucket.key', ''),
            'consumer_secret': settings.get(
                'authomatic.pr.bitbucket.secret', '')
        }
    }
    return Authomatic(
        config=authomatic_conf, secret=settings['authomatic.secret'])
