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
                'email_title': "App Enlight :: New password request"
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
                      'email_title': "App Enlight :: Start information"}
        UserService.send_email(
            request, recipients=[new_user.email], variables=email_vars,
            template='/email_templates/registered.jinja2')
        request.session.flash(_('You have successfully registered.'))
        DBSession.flush()
        headers = security.remember(request, new_user.id)
        return HTTPFound(location=request.route_url('/'),
                         headers=headers)
    return {
        "form": form,
        "sign_in_form": sign_in_form
    }


@view_config(route_name='/',
             renderer='appenlight:templates/dashboard/index.jinja2',
             permission=NO_PERMISSION_REQUIRED)
@view_config(route_name='angular_app_ui',
             renderer='appenlight:templates/dashboard/index.jinja2',
             permission=NO_PERMISSION_REQUIRED)
@view_config(route_name='angular_app_ui_ix',
             renderer='appenlight:templates/dashboard/index.jinja2',
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

    if request.user:
        request.user.last_login_date = datetime.datetime.utcnow()
        applications = request.user.resources_with_perms(
            ['view'], resource_types=['application'])
        # convert for angular
        applications = dict(
            [(a.resource_id, a.resource_name) for a in applications.all()]
        )
    else:
        applications = {}
    return {
        'applications': applications
    }
