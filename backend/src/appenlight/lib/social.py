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
