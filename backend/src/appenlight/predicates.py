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

import logging
from appenlight.forms import CSRFException

log = logging.getLogger(__name__)

from pyramid.interfaces import IDefaultCSRFOptions
from pyramid.session import (
    check_csrf_origin,
    check_csrf_token,
)

# taken directly from pyramid 1.7
# pyramid/viewderivers.py
# the difference is this deriver will ignore csrf_check when auth token
# policy is in effect

def csrf_view(view, info):
    explicit_val = info.options.get('require_csrf')
    defaults = info.registry.queryUtility(IDefaultCSRFOptions)
    if defaults is None:
        default_val = False
        token = 'csrf_token'
        header = 'X-CSRF-Token'
        safe_methods = frozenset(["GET", "HEAD", "OPTIONS", "TRACE"])
    else:
        default_val = defaults.require_csrf
        token = defaults.token
        header = defaults.header
        safe_methods = defaults.safe_methods
    enabled = (
        explicit_val is True or
        (explicit_val is not False and default_val)
    )
    # disable if both header and token are disabled
    enabled = enabled and (token or header)
    wrapped_view = view
    if enabled:
        def csrf_view(context, request):
            is_from_auth_token = 'auth:auth_token' in \
                                 request.effective_principals
            if is_from_auth_token:
                log.debug('ignoring CSRF check, auth token used')
            elif (
                request.method not in safe_methods and
                (
                # skip exception views unless value is explicitly defined
                        getattr(request, 'exception', None) is None or
                        explicit_val is not None
                )
            ):
                check_csrf_origin(request, raises=True)
                check_csrf_token(request, token, header, raises=True)
            return view(context, request)

        wrapped_view = csrf_view
    return wrapped_view

csrf_view.options = ('require_csrf',)


class PublicReportGroup(object):
    def __init__(self, val, config):
        self.val = val

    def text(self):
        return 'public_report_group = %s' % (self.val,)

    phash = text

    def __call__(self, context, request):
        report_group = getattr(context, 'report_group', None)
        if report_group:
            return context.report_group.public == self.val


class contextTypeClass(object):
    def __init__(self, context_property, config):
        self.context_property = context_property[0]
        self.cls = context_property[1]

    def text(self):
        return 'context_type_class = %s, %s' % (
            self.context_property, self.cls)

    phash = text

    def __call__(self, context, request):
        to_check = getattr(context, self.context_property, None)
        return isinstance(to_check, self.cls)


def unauthed_report_predicate(context, request):
    """
    This allows the user to access the view if context object public
    flag is True
    """
    if context.public:
        return True


def unauthed_report_predicate_inv(context, request):
    """
    This allows the user to access the view if context object public
    flag is NOT True
    """
    if context.public:
        return False
    return True


def unauthed_report_predicate(context, request):
    """
    This allows the user to access the view if context object public
    flag is True
    """
    if context.public:
        return True


def unauthed_report_predicate_inv(context, request):
    """
    This allows the user to access the view if context object public
    flag is NOT True
    """
    if context.public:
        return False
    return True
