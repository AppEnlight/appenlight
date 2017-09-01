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

import colander
import datetime
import json
import logging
import uuid
import pyramid.security as security
import appenlight.lib.helpers as h

from authomatic.adapters import WebObAdapter
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound, HTTPUnprocessableEntity
from pyramid.httpexceptions import HTTPNotFound, HTTPBadRequest
from pyramid.security import NO_PERMISSION_REQUIRED
from ziggurat_foundations.models.services.external_identity import \
    ExternalIdentityService

from appenlight.lib import generate_random_string
from appenlight.lib.social import handle_social_data
from appenlight.lib.utils import channelstream_request, add_cors_headers, \
    permission_tuple_to_dict
from appenlight.models import DBSession
from appenlight.models.alert_channels.email import EmailAlertChannel
from appenlight.models.alert_channel_action import AlertChannelAction
from appenlight.models.services.alert_channel import AlertChannelService
from appenlight.models.services.alert_channel_action import \
    AlertChannelActionService
from appenlight.models.auth_token import AuthToken
from appenlight.models.report import REPORT_TYPE_MATRIX
from appenlight.models.user import User
from appenlight.models.services.user import UserService
from appenlight.subscribers import _
from appenlight.validators import build_rule_schema
from appenlight import forms
from webob.multidict import MultiDict

log = logging.getLogger(__name__)


@view_config(route_name='users_no_id', renderer='json',
             request_method="GET", permission='root_administration')
def users_list(request):
    """
    Returns users list
    """
    props = ['user_name', 'id', 'first_name', 'last_name', 'email',
             'last_login_date', 'status']
    users = UserService.all()
    users_dicts = []
    for user in users:
        u_dict = user.get_dict(include_keys=props)
        u_dict['gravatar_url'] = user.gravatar_url(s=20)
        users_dicts.append(u_dict)
    return users_dicts


@view_config(route_name='users_no_id', renderer='json',
             request_method="POST", permission='root_administration')
def users_create(request):
    """
    Returns users list
    """
    form = forms.UserCreateForm(MultiDict(request.safe_json_body or {}),
                                csrf_context=request)
    if form.validate():
        log.info('registering user')
        user = User()
        # insert new user here
        DBSession.add(user)
        form.populate_obj(user)
        user.regenerate_security_code()
        user.set_password(user.user_password)
        user.status = 1 if form.status.data else 0
        request.session.flash(_('User created'))
        DBSession.flush()
        return user.get_dict(exclude_keys=['security_code_date', 'notes',
                                           'security_code', 'user_password'])
    else:
        return HTTPUnprocessableEntity(body=form.errors_json)


@view_config(route_name='users', renderer='json',
             request_method="GET", permission='root_administration')
@view_config(route_name='users', renderer='json',
             request_method="PATCH", permission='root_administration')
def users_update(request):
    """
    Updates user object
    """
    user = User.by_id(request.matchdict.get('user_id'))
    if not user:
        return HTTPNotFound()
    post_data = request.safe_json_body or {}
    if request.method == 'PATCH':
        form = forms.UserUpdateForm(MultiDict(post_data),
                                    csrf_context=request)
        if form.validate():
            form.populate_obj(user, ignore_none=True)
            if form.user_password.data:
                user.set_password(user.user_password)
            if form.status.data:
                user.status = 1
            else:
                user.status = 0
        else:
            return HTTPUnprocessableEntity(body=form.errors_json)
    return user.get_dict(exclude_keys=['security_code_date', 'notes',
                                       'security_code', 'user_password'])


@view_config(route_name='users_property',
             match_param='key=resource_permissions',
             renderer='json', permission='authenticated')
def users_resource_permissions_list(request):
    """
    Get list of permissions assigned to specific resources
    """
    user = User.by_id(request.matchdict.get('user_id'))
    if not user:
        return HTTPNotFound()
    return [permission_tuple_to_dict(perm) for perm in
            user.resources_with_possible_perms()]


@view_config(route_name='users', renderer='json',
             request_method="DELETE", permission='root_administration')
def users_DELETE(request):
    """
    Removes a user permanently from db - makes a check to see if after the
    operation there will be at least one admin left
    """
    msg = _('There needs to be at least one administrator in the system')
    user = User.by_id(request.matchdict.get('user_id'))
    if user:
        users = User.users_for_perms(['root_administration']).all()
        if len(users) < 2 and user.id == users[0].id:
            request.session.flash(msg, 'warning')
        else:
            DBSession.delete(user)
            request.session.flash(_('User removed'))
            return True
    request.response.status = 422
    return False


@view_config(route_name='users_self', renderer='json',
             request_method="GET", permission='authenticated')
@view_config(route_name='users_self', renderer='json',
             request_method="PATCH", permission='authenticated')
def users_self(request):
    """
    Updates user personal information
    """

    if request.method == 'PATCH':
        form = forms.gen_user_profile_form()(
            MultiDict(request.unsafe_json_body),
            csrf_context=request)
        if form.validate():
            form.populate_obj(request.user)
            request.session.flash(_('Your profile got updated.'))
        else:
            return HTTPUnprocessableEntity(body=form.errors_json)
    return request.user.get_dict(
        exclude_keys=['security_code_date', 'notes', 'security_code',
                      'user_password'],
        extended_info=True)


@view_config(route_name='users_self_property',
             match_param='key=external_identities', renderer='json',
             request_method='GET', permission='authenticated')
def users_external_identies(request):
    user = request.user
    identities = [{'provider': ident.provider_name,
                   'id': ident.external_user_name} for ident
                  in user.external_identities.all()]
    return identities


@view_config(route_name='users_self_property',
             match_param='key=external_identities', renderer='json',
             request_method='DELETE', permission='authenticated')
def users_external_identies_DELETE(request):
    """
    Unbinds external identities(google,twitter etc.) from user account
    """
    user = request.user
    for identity in user.external_identities.all():
        log.info('found identity %s' % identity)
        if (identity.provider_name == request.params.get('provider') and
                    identity.external_user_name == request.params.get('id')):
            log.info('remove identity %s' % identity)
            DBSession.delete(identity)
            return True
    return False


@view_config(route_name='users_self_property',
             match_param='key=password', renderer='json',
             request_method='PATCH', permission='authenticated')
def users_password(request):
    """
    Sets new password for user account
    """
    user = request.user
    form = forms.ChangePasswordForm(MultiDict(request.unsafe_json_body),
                                    csrf_context=request)
    form.old_password.user = user
    if form.validate():
        user.regenerate_security_code()
        user.set_password(form.new_password.data)
        msg = 'Your password got updated. ' \
              'Next time log in with your new credentials.'
        request.session.flash(_(msg))
        return True
    else:
        return HTTPUnprocessableEntity(body=form.errors_json)
    return False


@view_config(route_name='users_self_property', match_param='key=websocket',
             renderer='json', permission='authenticated')
def users_websocket(request):
    """
    Handle authorization of users trying to connect
    """
    # handle preflight request
    user = request.user
    if request.method == 'OPTIONS':
        res = request.response.body('OK')
        add_cors_headers(res)
        return res
    applications = user.resources_with_perms(
        ['view'], resource_types=['application'])
    channels = ['app_%s' % app.resource_id for app in applications]
    payload = {"username": user.user_name,
               "conn_id": str(uuid.uuid4()),
               "channels": channels
               }
    settings = request.registry.settings
    response = channelstream_request(
        settings['cometd.secret'], '/connect', payload,
        servers=[request.registry.settings['cometd_servers']],
        throw_exceptions=True)
    return payload


@view_config(route_name='users_self_property', request_method="GET",
             match_param='key=alert_channels', renderer='json',
             permission='authenticated')
def alert_channels(request):
    """
    Lists all available alert channels
    """
    user = request.user
    return [c.get_dict(extended_info=True) for c in user.alert_channels]


@view_config(route_name='users_self_property', match_param='key=alert_actions',
             request_method="GET", renderer='json', permission='authenticated')
def alert_actions(request):
    """
    Lists all available alert channels
    """
    user = request.user
    return [r.get_dict(extended_info=True) for r in user.alert_actions]


@view_config(route_name='users_self_property', renderer='json',
             match_param='key=alert_channels_rules', request_method='POST',
             permission='authenticated')
def alert_channels_rule_POST(request):
    """
    Creates new notification rule for specific alert channel
    """
    user = request.user
    alert_action = AlertChannelAction(owner_id=request.user.id,
                                      type='report')
    DBSession.add(alert_action)
    DBSession.flush()
    return alert_action.get_dict()


@view_config(route_name='users_self_property', permission='authenticated',
             match_param='key=alert_channels_rules',
             renderer='json', request_method='DELETE')
def alert_channels_rule_DELETE(request):
    """
    Removes specific alert channel rule
    """
    user = request.user
    rule_action = AlertChannelActionService.by_owner_id_and_pkey(
        user.id,
        request.GET.get('pkey'))
    if rule_action:
        DBSession.delete(rule_action)
        return True
    return HTTPNotFound()


@view_config(route_name='users_self_property', permission='authenticated',
             match_param='key=alert_channels_rules',
             renderer='json', request_method='PATCH')
def alert_channels_rule_PATCH(request):
    """
    Removes specific alert channel rule
    """
    user = request.user
    json_body = request.unsafe_json_body

    schema = build_rule_schema(json_body['rule'], REPORT_TYPE_MATRIX)
    try:
        schema.deserialize(json_body['rule'])
    except colander.Invalid as exc:
        return HTTPUnprocessableEntity(body=json.dumps(exc.asdict()))

    rule_action = AlertChannelActionService.by_owner_id_and_pkey(
        user.id,
        request.GET.get('pkey'))

    if rule_action:
        rule_action.rule = json_body['rule']
        rule_action.resource_id = json_body['resource_id']
        rule_action.action = json_body['action']
        return rule_action.get_dict()
    return HTTPNotFound()


@view_config(route_name='users_self_property', permission='authenticated',
             match_param='key=alert_channels',
             renderer='json', request_method='PATCH')
def alert_channels_PATCH(request):
    user = request.user
    channel_name = request.GET.get('channel_name')
    channel_value = request.GET.get('channel_value')
    # iterate over channels
    channel = None
    for channel in user.alert_channels:
        if (channel.channel_name == channel_name and
                    channel.channel_value == channel_value):
            break
    if not channel:
        return HTTPNotFound()

    allowed_keys = ['daily_digest', 'send_alerts']
    for k, v in request.unsafe_json_body.items():
        if k in allowed_keys:
            setattr(channel, k, v)
        else:
            return HTTPBadRequest()
    return channel.get_dict()


@view_config(route_name='users_self_property', permission='authenticated',
             match_param='key=alert_channels',
             request_method="POST", renderer='json')
def alert_channels_POST(request):
    """
    Creates a new email alert channel for user, sends a validation email
    """
    user = request.user
    form = forms.EmailChannelCreateForm(MultiDict(request.unsafe_json_body),
                                        csrf_context=request)
    if not form.validate():
        return HTTPUnprocessableEntity(body=form.errors_json)

    email = form.email.data.strip()
    channel = EmailAlertChannel()
    channel.channel_name = 'email'
    channel.channel_value = email
    security_code = generate_random_string(10)
    channel.channel_json_conf = {'security_code': security_code}
    user.alert_channels.append(channel)

    email_vars = {'user': user,
                  'email': email,
                  'request': request,
                  'security_code': security_code,
                  'email_title': "AppEnlight :: "
                                 "Please authorize your email"}

    UserService.send_email(request, recipients=[email],
                           variables=email_vars,
                           template='/email_templates/authorize_email.jinja2')
    request.session.flash(_('Your alert channel was '
                            'added to the system.'))
    request.session.flash(
        _('You need to authorize your email channel, a message was '
          'sent containing necessary information.'),
        'warning')
    DBSession.flush()
    channel.get_dict()


@view_config(route_name='section_view',
             match_param=['section=user_section',
                          'view=alert_channels_authorize'],
             renderer='string', permission='authenticated')
def alert_channels_authorize(request):
    """
    Performs alert channel authorization based on auth code sent in email
    """
    user = request.user
    for channel in user.alert_channels:
        security_code = request.params.get('security_code', '')
        if channel.channel_json_conf['security_code'] == security_code:
            channel.channel_validated = True
            request.session.flash(_('Your email was authorized.'))
    return HTTPFound(location=request.route_url('/'))


@view_config(route_name='users_self_property', request_method="DELETE",
             match_param='key=alert_channels', renderer='json',
             permission='authenticated')
def alert_channel_DELETE(request):
    """
    Removes alert channel from users channel
    """
    user = request.user
    channel = None
    for chan in user.alert_channels:
        if (chan.channel_name == request.params.get('channel_name') and
                    chan.channel_value == request.params.get('channel_value')):
            channel = chan
            break
    if channel:
        user.alert_channels.remove(channel)
        request.session.flash(_('Your channel was removed.'))
        return True
    return False


@view_config(route_name='users_self_property', permission='authenticated',
             match_param='key=alert_channels_actions_binds',
             renderer='json', request_method="POST")
def alert_channels_actions_binds_POST(request):
    """
    Adds alert action to users channels
    """
    user = request.user
    json_body = request.unsafe_json_body
    channel = AlertChannelService.by_owner_id_and_pkey(
        user.id,
        json_body.get('channel_pkey'))

    rule_action = AlertChannelActionService.by_owner_id_and_pkey(
        user.id,
        json_body.get('action_pkey'))

    if channel and rule_action:
        if channel.pkey not in [c.pkey for c in rule_action.channels]:
            rule_action.channels.append(channel)
            return rule_action.get_dict(extended_info=True)
    return HTTPUnprocessableEntity()


@view_config(route_name='users_self_property', request_method="DELETE",
             match_param='key=alert_channels_actions_binds',
             renderer='json', permission='authenticated')
def alert_channels_actions_binds_DELETE(request):
    """
    Removes alert action from users channels
    """
    user = request.user
    channel = AlertChannelService.by_owner_id_and_pkey(
        user.id,
        request.GET.get('channel_pkey'))

    rule_action = AlertChannelActionService.by_owner_id_and_pkey(
        user.id,
        request.GET.get('action_pkey'))

    if channel and rule_action:
        if channel.pkey in [c.pkey for c in rule_action.channels]:
            rule_action.channels.remove(channel)
            return rule_action.get_dict(extended_info=True)
    return HTTPUnprocessableEntity()


@view_config(route_name='social_auth_abort',
             renderer='string', permission=NO_PERMISSION_REQUIRED)
def oauth_abort(request):
    """
    Handles problems with authorization via velruse
    """


@view_config(route_name='social_auth', permission=NO_PERMISSION_REQUIRED)
def social_auth(request):
    # Get the internal provider name URL variable.
    provider_name = request.matchdict.get('provider')

    # Start the login procedure.
    adapter = WebObAdapter(request, request.response)
    result = request.authomatic.login(adapter, provider_name)
    if result:
        if result.error:
            return handle_auth_error(request, result)
        elif result.user:
            return handle_auth_success(request, result)
    return request.response


def handle_auth_error(request, result):
    # Login procedure finished with an error.
    request.session.pop('zigg.social_auth', None)
    request.session.flash(_('Something went wrong when we tried to '
                            'authorize you via external provider. '
                            'Please try again.'), 'warning')

    return HTTPFound(location=request.route_url('/'))


def handle_auth_success(request, result):
    # Hooray, we have the user!
    # OAuth 2.0 and OAuth 1.0a provide only limited user data on login,
    # We need to update the user to get more info.
    if result.user:
        result.user.update()

    social_data = {
        'user': {'data': result.user.data},
        'credentials': result.user.credentials
    }
    # normalize data
    social_data['user']['id'] = result.user.id
    user_name = result.user.username or ''
    # use email name as username for google
    if (social_data['credentials'].provider_name == 'google' and
            result.user.email):
        user_name = result.user.email
    social_data['user']['user_name'] = user_name
    social_data['user']['email'] = result.user.email or ''

    request.session['zigg.social_auth'] = social_data
    # user is logged so bind his external identity with account
    if request.user:
        handle_social_data(request, request.user, social_data)
        request.session.pop('zigg.social_auth', None)
        return HTTPFound(location=request.route_url('/'))
    else:
        user = ExternalIdentityService.user_by_external_id_and_provider(
            social_data['user']['id'],
            social_data['credentials'].provider_name
        )
        # fix legacy accounts with wrong google ID
        if not user and social_data['credentials'].provider_name == 'google':
            user = ExternalIdentityService.user_by_external_id_and_provider(
                social_data['user']['email'],
                social_data['credentials'].provider_name)

        # user tokens are already found in our db
        if user:
            handle_social_data(request, user, social_data)
            headers = security.remember(request, user.id)
            request.session.pop('zigg.social_auth', None)
            return HTTPFound(location=request.route_url('/'), headers=headers)
        else:
            msg = 'You need to finish registration ' \
                  'process to bind your external identity to your account ' \
                  'or sign in to existing account'
            request.session.flash(msg)
            return HTTPFound(location=request.route_url('register'))


@view_config(route_name='section_view', permission='authenticated',
             match_param=['section=users_section', 'view=search_users'],
             renderer='json')
def search_users(request):
    """
    Returns a list of users for autocomplete
    """
    user = request.user
    items_returned = []
    like_condition = request.params.get('user_name', '') + '%'
    # first append used if email is passed
    found_user = User.by_email(request.params.get('user_name', ''))
    if found_user:
        name = '{} {}'.format(found_user.first_name, found_user.last_name)
        items_returned.append({'user': found_user.user_name, 'name': name})
    for found_user in User.user_names_like(like_condition).limit(20):
        name = '{} {}'.format(found_user.first_name, found_user.last_name)
        items_returned.append({'user': found_user.user_name, 'name': name})
    return items_returned


@view_config(route_name='users_self_property', match_param='key=auth_tokens',
             request_method="GET", renderer='json', permission='authenticated')
@view_config(route_name='users_property', match_param='key=auth_tokens',
             request_method="GET", renderer='json', permission='authenticated')
def auth_tokens_list(request):
    """
    Lists all available alert channels
    """
    if request.matched_route.name == 'users_self_property':
        user = request.user
    else:
        user = User.by_id(request.matchdict.get('user_id'))
        if not user:
            return HTTPNotFound()
    return [c.get_dict() for c in user.auth_tokens]


@view_config(route_name='users_self_property', match_param='key=auth_tokens',
             request_method="POST", renderer='json',
             permission='authenticated')
@view_config(route_name='users_property', match_param='key=auth_tokens',
             request_method="POST", renderer='json',
             permission='authenticated')
def auth_tokens_POST(request):
    """
    Lists all available alert channels
    """
    if request.matched_route.name == 'users_self_property':
        user = request.user
    else:
        user = User.by_id(request.matchdict.get('user_id'))
        if not user:
            return HTTPNotFound()

    req_data = request.safe_json_body or {}
    if not req_data.get('expires'):
        req_data.pop('expires', None)
    form = forms.AuthTokenCreateForm(MultiDict(req_data), csrf_context=request)
    if not form.validate():
        return HTTPUnprocessableEntity(body=form.errors_json)
    token = AuthToken()
    form.populate_obj(token)
    if token.expires:
        interval = h.time_deltas.get(token.expires)['delta']
        token.expires = datetime.datetime.utcnow() + interval
    user.auth_tokens.append(token)
    DBSession.flush()
    return token.get_dict()


@view_config(route_name='users_self_property', match_param='key=auth_tokens',
             request_method="DELETE", renderer='json',
             permission='authenticated')
@view_config(route_name='users_property', match_param='key=auth_tokens',
             request_method="DELETE", renderer='json',
             permission='authenticated')
def auth_tokens_DELETE(request):
    """
    Lists all available alert channels
    """
    if request.matched_route.name == 'users_self_property':
        user = request.user
    else:
        user = User.by_id(request.matchdict.get('user_id'))
        if not user:
            return HTTPNotFound()

    for token in user.auth_tokens:
        if token.token == request.params.get('token'):
            user.auth_tokens.remove(token)
            return True
    return False
