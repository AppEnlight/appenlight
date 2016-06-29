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

from pyramid.security import Allow, Everyone, Authenticated, ALL_PERMISSIONS
from pyramid.authentication import CallbackAuthenticationPolicy
import appenlight.models.resource
from appenlight.models.services.auth_token import AuthTokenService
from appenlight.models.services.application import ApplicationService
from appenlight.models.services.report_group import ReportGroupService
from appenlight.models.services.plugin_config import PluginConfigService
from appenlight.lib import to_integer_safe
from pyramid.httpexceptions import HTTPNotFound, HTTPBadRequest
from ziggurat_foundations.permissions import permission_to_04_acls
import defusedxml.ElementTree as ElementTree
import urllib.request, urllib.error, urllib.parse
import logging
import re
from xml.sax.saxutils import quoteattr

log = logging.getLogger(__name__)


def groupfinder(userid, request):
    if userid and hasattr(request, 'user') and request.user:
        groups = ['group:%s' % g.id for g in request.user.groups]
        return groups
    return []


class AuthTokenAuthenticationPolicy(CallbackAuthenticationPolicy):
    def __init__(self, callback=None):
        self.callback = callback

    def remember(self, request, principal, **kw):
        return []

    def forget(self, request):
        return []

    def unauthenticated_userid(self, request):
        token = request.headers.get('x-appenlight-auth-token')
        if token:
            auth_token = AuthTokenService.by_token(token)
            if auth_token and not auth_token.is_expired:
                log.info('%s is valid' % auth_token)
                return auth_token.owner_id
            elif auth_token:
                log.warning('%s is expired' % auth_token)
            else:
                log.warning('token: %s is not found' % token)

    def authenticated_userid(self, request):
        return self.unauthenticated_userid(request)


def rewrite_root_perm(perm_user, perm_name):
    """
    Translates root_administration into ALL_PERMISSIONS object
    """
    if perm_name == 'root_administration':
        return (Allow, perm_user, ALL_PERMISSIONS,)
    else:
        return (Allow, perm_user, perm_name,)


def add_root_superperm(request, context):
    """
    Adds ALL_PERMISSIONS to every resource if user somehow has 'root_permission'
    non-resource permission
    """
    if hasattr(request, 'user') and request.user:
        acls = permission_to_04_acls(request.user.permissions)
        for perm_user, perm_name in acls:
            if perm_name == 'root_administration':
                context.__acl__.append(rewrite_root_perm(perm_user, perm_name))


class RootFactory(object):
    """
    General factory for non-resource/report specific pages
    """

    def __init__(self, request):
        self.__acl__ = [(Allow, Authenticated, 'authenticated'),
                        (Allow, Authenticated, 'create_resources')]
        # general page factory - append custom non resource permissions
        if hasattr(request, 'user') and request.user:
            acls = permission_to_04_acls(request.user.permissions)
            for perm_user, perm_name in acls:
                self.__acl__.append(rewrite_root_perm(perm_user, perm_name))

class ResourceFactory(object):
    """
    Checks permissions to specific resource based on user permissions or
    API key headers
    """

    def __init__(self, request):
        Resource = appenlight.models.resource.Resource

        self.__acl__ = []
        resource_id = request.matchdict.get("resource_id",
                                            request.GET.get("resource_id"))
        resource_id = to_integer_safe(resource_id)
        self.resource = Resource.by_resource_id(resource_id) \
            if resource_id else None
        if self.resource and request.user:
            self.__acl__ = self.resource.__acl__
            permissions = self.resource.perms_for_user(request.user)
            for perm_user, perm_name in permission_to_04_acls(permissions):
                self.__acl__.append(rewrite_root_perm(perm_user, perm_name))
        add_root_superperm(request, self)


class ResourceReportFactory(object):
    """
    Checks permissions to specific resource based on user permissions or
    API key headers
    Resource is fetched based on report group information
    """

    def __init__(self, request):
        Resource = appenlight.models.resource.Resource

        self.__acl__ = []
        group_id = request.matchdict.get("group_id",
                                         request.params.get("group_id"))
        group_id = to_integer_safe(group_id)
        self.report_group = ReportGroupService.by_id(
            group_id) if group_id else None
        if not self.report_group:
            raise HTTPNotFound()

        self.public = self.report_group.public
        self.resource = Resource.by_resource_id(self.report_group.resource_id) \
            if self.report_group else None

        if self.resource:
            self.__acl__ = self.resource.__acl__
        if request.user:
            permissions = self.resource.perms_for_user(request.user)
            for perm_user, perm_name in permission_to_04_acls(permissions):
                self.__acl__.append(rewrite_root_perm(perm_user, perm_name))
        if self.public:
            self.__acl__.append((Allow, Everyone, 'view',))
        if not request.user:
            # unauthed users need to visit using both group and report pair
            report_id = request.params.get('reportId',
                                           request.params.get('report_id', -1))
            report = self.report_group.get_report(report_id, public=True)
            if not report:
                raise HTTPNotFound()
        add_root_superperm(request, self)


class APIFactory(object):
    """
    Checks permissions to perform client API actions based on keys
    """

    def __init__(self, request):
        self.__acl__ = []
        self.possibly_public = False
        private_api_key = request.headers.get(
            'x-appenlight-api-key',
            request.params.get('api_key')
        )
        log.debug("private key: %s" % private_api_key)
        if private_api_key:
            self.resource = ApplicationService.by_api_key_cached()(
                private_api_key)
        # then try public key
        else:
            public_api_key = request.headers.get(
                'x-appenlight-public-api-key',
                request.GET.get('public_api_key'))
            log.debug("public key: %s" % public_api_key)
            self.resource = ApplicationService.by_public_api_key(
                public_api_key, from_cache=True, request=request)
            self.possibly_public = True
        if self.resource:
            self.__acl__.append((Allow, Everyone, 'create',))


class AirbrakeV2APIFactory(object):
    """
    Check permission based on Airbrake XML report
    """

    def __init__(self, request):
        self.__acl__ = []
        self.possibly_public = False
        fixed_xml_data = ''
        try:
            data = request.GET.get('data')
            if data:
                self.possibly_public = True
        except (UnicodeDecodeError, UnicodeEncodeError) as exc:
            log.warning(
                'Problem parsing Airbrake data: %s, failed decoding' % exc)
            raise HTTPBadRequest()
        try:
            if not data:
                data = request.body
                # fix shitty airbrake js client not escaping line method attr

            def repl(input):
                return 'line method=%s file' % quoteattr(input.group(1))

            fixed_xml_data = re.sub('line method="(.*?)" file', repl, data)
            root = ElementTree.fromstring(fixed_xml_data)
        except Exception as exc:
            log.info(
                'Problem parsing Airbrake '
                'data: %s, trying unquoting' % exc)
            self.possibly_public = True
            try:
                root = ElementTree.fromstring(urllib.parse.unquote(fixed_xml_data))
            except Exception as exc:
                log.warning('Problem parsing Airbrake '
                            'data: %s, failed completly' % exc)
                raise HTTPBadRequest()
        self.airbrake_xml_etree = root
        api_key = root.findtext('api-key', '')

        self.resource = ApplicationService.by_api_key_cached()(api_key)
        if not self.resource:
            self.resource = ApplicationService.by_public_api_key(api_key,
                                                                 from_cache=True,
                                                                 request=request)
            if self.resource:
                self.possibly_public = True

        if self.resource:
            self.__acl__.append((Allow, Everyone, 'create',))


def parse_sentry_header(header):
    parsed = header.split(' ', 1)[1].split(',') or []
    return dict([x.strip().split('=') for x in parsed])


class SentryAPIFactory(object):
    """
    Check permission based on Sentry payload
    """

    def __init__(self, request):
        self.__acl__ = []
        self.possibly_public = False
        if request.headers.get('X-Sentry-Auth', '').startswith('Sentry'):
            header_string = request.headers['X-Sentry-Auth']
            result = parse_sentry_header(header_string)
        elif request.headers.get('Authorization', '').startswith('Sentry'):
            header_string = request.headers['Authorization']
            result = parse_sentry_header(header_string)
        else:
            result = dict((k, v) for k, v in list(request.GET.items())
                          if k.startswith('sentry_'))
        key = result.get('sentry_key')
        log.info('sentry request {}'.format(result))

        self.resource = ApplicationService.by_api_key_cached()(key)
        if not self.resource or \
            result.get('sentry_client', '').startswith('raven-js'):
            self.resource = ApplicationService.by_public_api_key(
                key, from_cache=True, request=request)
        if self.resource:
            self.__acl__.append((Allow, Everyone, 'create',))


class ResourcePluginConfigFactory(object):

    def __init__(self, request):
        Resource = appenlight.models.resource.Resource
        self.__acl__ = []
        self.resource = None
        plugin_id = to_integer_safe(request.matchdict.get('id'))
        self.plugin = PluginConfigService.by_id(plugin_id)
        if not self.plugin:
            raise HTTPNotFound()
        if self.plugin.resource_id:
            self.resource = Resource.by_resource_id(self.plugin.resource_id)
        if self.resource:
            self.__acl__ = self.resource.__acl__
        if request.user and self.resource:
            permissions = self.resource.perms_for_user(request.user)
            for perm_user, perm_name in permission_to_04_acls(permissions):
                self.__acl__.append(rewrite_root_perm(perm_user, perm_name))

        add_root_superperm(request, self)


class ResourceJSONBodyFactory(object):
    """
    Checks permissions to specific resource based on user permissions or
    API key headers from json body
    """

    def __init__(self, request):
        Resource = appenlight.models.resource.Resource

        self.__acl__ = []
        resource_id = request.unsafe_json_body().get('resource_id')
        resource_id = to_integer_safe(resource_id)
        self.resource = Resource.by_resource_id(resource_id)
        if self.resource and request.user:
            self.__acl__ = self.resource.__acl__
            permissions = self.resource.perms_for_user(request.user)
            for perm_user, perm_name in permission_to_04_acls(permissions):
                self.__acl__.append(rewrite_root_perm(perm_user, perm_name))
        add_root_superperm(request, self)


class ResourcePluginMixedFactory(object):
    def __init__(self, request):
        Resource = appenlight.models.resource.Resource
        self.__acl__ = []
        json_body = request.safe_json_body
        self.resource = None
        if json_body:
            resource_id = json_body.get('resource_id')
        else:
            resource_id = request.GET.get('resource_id')
        if resource_id:
            resource_id = to_integer_safe(resource_id)
            self.resource = Resource.by_resource_id(resource_id)
        if self.resource and request.user:
            self.__acl__ = self.resource.__acl__
            permissions = self.resource.perms_for_user(request.user)
            for perm_user, perm_name in permission_to_04_acls(permissions):
                self.__acl__.append(rewrite_root_perm(perm_user, perm_name))
        add_root_superperm(request, self)
