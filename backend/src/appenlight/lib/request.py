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

import json

from pyramid.security import unauthenticated_userid

import appenlight.lib.helpers as helpers

from authomatic.providers import oauth2, oauth1
from authomatic import Authomatic
from ziggurat_foundations.models.services.user import UserService


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
            user = UserService.by_id(user_id)
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
