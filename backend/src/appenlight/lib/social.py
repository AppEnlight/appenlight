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

from ziggurat_foundations.models.services.external_identity import \
    ExternalIdentityService
from appenlight.models.external_identity import ExternalIdentity


def handle_social_data(request, user, social_data):
    social_data = social_data
    update_identity = False

    extng_id = ExternalIdentityService.by_external_id_and_provider(
        social_data['user']['id'],
        social_data['credentials'].provider_name
    )

    # fix legacy accounts with wrong google ID
    if not extng_id and social_data['credentials'].provider_name == 'google':
        extng_id = ExternalIdentityService.by_external_id_and_provider(
            social_data['user']['email'],
            social_data['credentials'].provider_name
        )

    if extng_id:
        extng_id.delete()
        update_identity = True

    if not social_data['user']['id']:
        request.session.flash(
            'No external user id found? Perhaps permissions for '
            'authentication are set incorrectly', 'error')
        return False

    if not extng_id or update_identity:
        if not update_identity:
            request.session.flash('Your external identity is now '
                                  'connected with your account')
        ex_identity = ExternalIdentity()
        ex_identity.external_id = social_data['user']['id']
        ex_identity.external_user_name = social_data['user']['user_name']
        ex_identity.provider_name = social_data['credentials'].provider_name
        ex_identity.access_token = social_data['credentials'].token
        ex_identity.token_secret = social_data['credentials'].token_secret
        ex_identity.alt_token = social_data['credentials'].refresh_token
        user.external_identities.append(ex_identity)
        request.session.pop('zigg.social_auth', None)
