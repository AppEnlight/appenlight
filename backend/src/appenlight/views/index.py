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

import datetime
import logging
import uuid

import pyramid.security as security

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.response import Response
from pyramid.security import NO_PERMISSION_REQUIRED
from ziggurat_foundations.ext.pyramid.sign_in import ZigguratSignInSuccess
from ziggurat_foundations.ext.pyramid.sign_in import ZigguratSignInBadAuth
from ziggurat_foundations.ext.pyramid.sign_in import ZigguratSignOut

from appenlight.lib.social import handle_social_data
from appenlight.models import DBSession
from appenlight.models.user import User
from appenlight.models.services.user import UserService
from appenlight.subscribers import _
from appenlight import forms
from webob.multidict import MultiDict

log = logging.getLogger(__name__)


@view_config(context=ZigguratSignInSuccess, permission=NO_PERMISSION_REQUIRED)
def sign_in(request):
    """
    Performs sign in by sending proper user identification headers
    Regenerates CSRF token
    """
    user = request.context.user
    if user.status == 1:
        request.session.new_csrf_token()
        user.last_login_date = datetime.datetime.utcnow()
        social_data = request.session.get('zigg.social_auth')
        if social_data:
            handle_social_data(request, user, social_data)
    else:
        request.session.flash(_('Account got disabled'))

    if request.context.came_from != '/':
        return HTTPFound(location=request.context.came_from,
                         headers=request.context.headers)
    else:
        return HTTPFound(location=request.route_url('/'),
                         headers=request.context.headers)


@view_config(context=ZigguratSignInBadAuth, permission=NO_PERMISSION_REQUIRED)
def bad_auth(request):
    """
    Handles incorrect login flow
    """
    request.session.flash(_('Incorrect username or password'), 'warning')
    return HTTPFound(location=request.route_url('register'),
                     headers=request.context.headers)


@view_config(context=ZigguratSignOut, permission=NO_PERMISSION_REQUIRED)
def sign_out(request):
    """
    Removes user identification cookie
    """
    return HTTPFound(location=request.route_url('register'),
                     headers=request.context.headers)


@view_config(route_name='lost_password',
             renderer='appenlight:templates/user/lost_password.jinja2',
             permission=NO_PERMISSION_REQUIRED)
def lost_password(request):
    """
    Presents lost password page - sends password reset link to
    specified email address.
    This link is valid only for 10 minutes
    """
    form = forms.LostPasswordForm(request.POST, csrf_context=request)
    if request.method == 'POST' and form.validate():
        user = User.by_email(form.email.data)
        if user:
            user.regenerate_security_code()
            user.security_code_date = datetime.datetime.utcnow()
            email_vars = {
                'user': user,
                'request': request,
                'email_title': "AppEnlight :: New password request"
            }
            UserService.send_email(
                request, recipients=[user.email],
                variables=email_vars,
                template='/email_templates/lost_password.jinja2')
            msg = 'Password reset email had been sent. ' \
                  'Please check your mailbox for further instructions.'
            request.session.flash(_(msg))
            return HTTPFound(location=request.route_url('lost_password'))
    return {"form": form}


@view_config(route_name='lost_password_generate',
             permission=NO_PERMISSION_REQUIRED,
             renderer='appenlight:templates/user/lost_password_generate.jinja2')
def lost_password_generate(request):
    """
    Shows new password form - perform time check and set new password for user
    """
    user = User.by_user_name_and_security_code(
        request.GET.get('user_name'), request.GET.get('security_code'))
    if user:
        delta = datetime.datetime.utcnow() - user.security_code_date

    if user and delta.total_seconds() < 600:
        form = forms.NewPasswordForm(request.POST, csrf_context=request)
        if request.method == "POST" and form.validate():
            user.set_password(form.new_password.data)
            request.session.flash(_('You can sign in with your new password.'))
            return HTTPFound(location=request.route_url('register'))
        else:
            return {"form": form}
    else:
        return Response('Security code expired')


@view_config(route_name='register',
             renderer='appenlight:templates/user/register.jinja2',
             permission=NO_PERMISSION_REQUIRED)
def register(request):
    """
    Render register page with form
    Also handles oAuth flow for registration
    """
    login_url = request.route_url('ziggurat.routes.sign_in')
    if request.query_string:
        query_string = '?%s' % request.query_string
    else:
        query_string = ''
    referrer = '%s%s' % (request.path, query_string)

    if referrer in [login_url, '/register', '/register?sign_in=1']:
        referrer = '/'  # never use the login form itself as came_from
    sign_in_form = forms.SignInForm(
        came_from=request.params.get('came_from', referrer),
        csrf_context=request)

    # populate form from oAuth session data returned by authomatic
    social_data = request.session.get('zigg.social_auth')
    if request.method != 'POST' and social_data:
        log.debug(social_data)
        user_name = social_data['user'].get('user_name', '').split('@')[0]
        form_data = {
            'user_name': user_name,
            'email': social_data['user'].get('email')
        }
        form_data['user_password'] = str(uuid.uuid4())
        form = forms.UserRegisterForm(MultiDict(form_data),
                                      csrf_context=request)
        form.user_password.widget.hide_value = False
    else:
        form = forms.UserRegisterForm(request.POST, csrf_context=request)
    if request.method == 'POST' and form.validate():
        log.info('registering user')
        # insert new user here
        if request.registry.settings['appenlight.disable_registration']:
            request.session.flash(_('Registration is currently disabled.'))
            return HTTPFound(location=request.route_url('/'))

        new_user = User()
        DBSession.add(new_user)
        form.populate_obj(new_user)
        new_user.regenerate_security_code()
        new_user.status = 1
        new_user.set_password(new_user.user_password)
        new_user.registration_ip = request.environ.get('REMOTE_ADDR')

        if social_data:
            handle_social_data(request, new_user, social_data)

        email_vars = {'user': new_user,
                      'request': request,
                      'email_title': "AppEnlight :: Start information"}
        UserService.send_email(
            request, recipients=[new_user.email], variables=email_vars,
            template='/email_templates/registered.jinja2')
        request.session.flash(_('You have successfully registered.'))
        DBSession.flush()
        headers = security.remember(request, new_user.id)
        return HTTPFound(location=request.route_url('/'),
                         headers=headers)
    settings = request.registry.settings
    social_plugins = {}
    if settings.get('authomatic.pr.twitter.key', ''):
        social_plugins['twitter'] = True
    if settings.get('authomatic.pr.google.key', ''):
        social_plugins['google'] = True
    if settings.get('authomatic.pr.github.key', ''):
        social_plugins['github'] = True
    if settings.get('authomatic.pr.bitbucket.key', ''):
        social_plugins['bitbucket'] = True

    return {
        "form": form,
        "sign_in_form": sign_in_form,
        "social_plugins": social_plugins
    }


@view_config(route_name='/',
             renderer='appenlight:templates/app.jinja2',
             permission=NO_PERMISSION_REQUIRED)
@view_config(route_name='angular_app_ui',
             renderer='appenlight:templates/app.jinja2',
             permission=NO_PERMISSION_REQUIRED)
@view_config(route_name='angular_app_ui_ix',
             renderer='appenlight:templates/app.jinja2',
             permission=NO_PERMISSION_REQUIRED)
def app_main_index(request):
    """
    Render dashoard/report browser page page along with:
     - flash messages
     - application list
     - assigned reports
     - latest events
     (those last two come from subscribers.py that sets global renderer variables)
    """
    return {}
