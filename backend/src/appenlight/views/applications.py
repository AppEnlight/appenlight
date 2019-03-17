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

import copy
import json
import logging

from datetime import datetime, timedelta

import colander
from pyramid.httpexceptions import HTTPFound, HTTPUnprocessableEntity
from pyramid.view import view_config
from webob.multidict import MultiDict
from zope.sqlalchemy import mark_changed
from ziggurat_foundations.permissions import ANY_PERMISSION

import appenlight.forms as forms
from appenlight.models import DBSession
from appenlight.models.resource import Resource
from appenlight.models.application import Application
from appenlight.models.application_postprocess_conf import ApplicationPostprocessConf
from ziggurat_foundations.models.services.user import UserService
from ziggurat_foundations.models.services.resource import ResourceService
from ziggurat_foundations.models.services.user_resource_permission import (
    UserResourcePermissionService,
)
from appenlight.models.user_resource_permission import UserResourcePermission
from appenlight.models.group_resource_permission import GroupResourcePermission
from appenlight.models.services.application import ApplicationService
from appenlight.models.services.application_postprocess_conf import (
    ApplicationPostprocessConfService,
)
from appenlight.models.services.group import GroupService
from appenlight.models.services.group_resource_permission import (
    GroupResourcePermissionService,
)
from appenlight.models.services.request_metric import RequestMetricService
from appenlight.models.services.report_group import ReportGroupService
from appenlight.models.services.slow_call import SlowCallService
from appenlight.lib import helpers as h
from appenlight.lib.utils import build_filter_settings_from_query_dict
from appenlight.security import RootFactory
from appenlight.models.report import REPORT_TYPE_MATRIX
from appenlight.validators import build_rule_schema

_ = str

log = logging.getLogger(__name__)


def app_not_found(request, id):
    """
    Redirects on non found and sets a flash message
    """
    request.session.flash(_("Application not found"), "warning")
    return HTTPFound(location=request.route_url("applications", action="index"))


@view_config(
    route_name="applications_no_id",
    renderer="json",
    request_method="GET",
    permission="authenticated",
)
def applications_list(request):
    """
    Applications list

    if query params contain ?type=foo, it will list applications
    with one of those permissions for user,
    otherwise only list of owned applications will
    be returned

    appending ?root_list while being administration will allow to list all
    applications in the system

    """
    is_root = request.has_permission("root_administration", RootFactory(request))
    if is_root and request.GET.get("root_list"):
        resources = Resource.all().order_by(Resource.resource_name)
        resource_type = request.GET.get("resource_type", "application")
        if resource_type:
            resources = resources.filter(Resource.resource_type == resource_type)
    else:
        permissions = request.params.getall("permission")
        if permissions:
            resources = UserService.resources_with_perms(
                request.user,
                permissions,
                resource_types=[request.GET.get("resource_type", "application")],
            )
        else:
            resources = request.user.resources.filter(
                Application.resource_type
                == request.GET.get("resource_type", "application")
            )
    return [
        r.get_dict(
            include_keys=[
                "resource_id",
                "resource_name",
                "domains",
                "owner_user_name",
                "owner_group_name",
            ]
        )
        for r in resources
    ]


@view_config(
    route_name="applications", renderer="json", request_method="GET", permission="view"
)
def application_GET(request):
    resource = request.context.resource
    include_sensitive_info = False
    if request.has_permission("edit"):
        include_sensitive_info = True
    resource_dict = resource.get_dict(
        include_perms=include_sensitive_info,
        include_processing_rules=include_sensitive_info,
    )
    return resource_dict


@view_config(
    route_name="applications_no_id",
    request_method="POST",
    renderer="json",
    permission="create_resources",
)
def application_create(request):
    """
    Creates new application instances
    """
    user = request.user
    form = forms.ApplicationCreateForm(
        MultiDict(request.unsafe_json_body), csrf_context=request
    )
    if form.validate():
        session = DBSession()
        resource = Application()
        DBSession.add(resource)
        form.populate_obj(resource)
        resource.api_key = resource.generate_api_key()
        user.resources.append(resource)
        request.session.flash(_("Application created"))
        DBSession.flush()
        mark_changed(session)
    else:
        return HTTPUnprocessableEntity(body=form.errors_json)

    return resource.get_dict()


@view_config(
    route_name="applications",
    request_method="PATCH",
    renderer="json",
    permission="edit",
)
def application_update(request):
    """
    Updates main application configuration
    """
    resource = request.context.resource
    if not resource:
        return app_not_found()

    # disallow setting permanent storage by non-admins
    # use default/non-resource based context for this check
    req_dict = copy.copy(request.unsafe_json_body)
    if not request.has_permission("root_administration", RootFactory(request)):
        req_dict["allow_permanent_storage"] = ""
    if not req_dict.get("uptime_url"):
        # needed cause validator is still triggered by default
        req_dict.pop("uptime_url", "")
    application_form = forms.ApplicationUpdateForm(
        MultiDict(req_dict), csrf_context=request
    )
    if application_form.validate():
        application_form.populate_obj(resource)
        request.session.flash(_("Application updated"))
    else:
        return HTTPUnprocessableEntity(body=application_form.errors_json)

    include_sensitive_info = False
    if request.has_permission("edit"):
        include_sensitive_info = True
    resource_dict = resource.get_dict(
        include_perms=include_sensitive_info,
        include_processing_rules=include_sensitive_info,
    )
    return resource_dict


@view_config(
    route_name="applications_property",
    match_param="key=api_key",
    request_method="POST",
    renderer="json",
    permission="delete",
)
def application_regenerate_key(request):
    """
    Regenerates API keys for application
    """
    resource = request.context.resource

    form = forms.CheckPasswordForm(
        MultiDict(request.unsafe_json_body), csrf_context=request
    )
    form.password.user = request.user

    if form.validate():
        resource.api_key = resource.generate_api_key()
        resource.public_key = resource.generate_api_key()
        msg = "API keys regenerated - please update your application config."
        request.session.flash(_(msg))
    else:
        return HTTPUnprocessableEntity(body=form.errors_json)

    if request.has_permission("edit"):
        include_sensitive_info = True
    resource_dict = resource.get_dict(
        include_perms=include_sensitive_info,
        include_processing_rules=include_sensitive_info,
    )
    return resource_dict


@view_config(
    route_name="applications_property",
    match_param="key=delete_resource",
    request_method="PATCH",
    renderer="json",
    permission="delete",
)
def application_remove(request):
    """
    Removes application resources
    """
    resource = request.context.resource
    # we need polymorphic object here, to properly launch sqlalchemy events
    resource = ApplicationService.by_id(resource.resource_id)
    form = forms.CheckPasswordForm(
        MultiDict(request.safe_json_body or {}), csrf_context=request
    )
    form.password.user = request.user
    if form.validate():
        DBSession.delete(resource)
        request.session.flash(_("Application removed"))
    else:
        return HTTPUnprocessableEntity(body=form.errors_json)

    return True


@view_config(
    route_name="applications_property",
    match_param="key=owner",
    request_method="PATCH",
    renderer="json",
    permission="delete",
)
def application_ownership_transfer(request):
    """
    Allows application owner to transfer application ownership to other user
    """
    resource = request.context.resource
    form = forms.ChangeApplicationOwnerForm(
        MultiDict(request.safe_json_body or {}), csrf_context=request
    )
    form.password.user = request.user
    if form.validate():
        user = UserService.by_user_name(form.user_name.data)
        user.resources.append(resource)
        # remove integrations to not leak security data of external applications
        for integration in resource.integrations[:]:
            resource.integrations.remove(integration)
        request.session.flash(_("Application transfered"))
    else:
        return HTTPUnprocessableEntity(body=form.errors_json)
    return True


@view_config(
    route_name="applications_property",
    match_param="key=postprocessing_rules",
    renderer="json",
    request_method="POST",
    permission="edit",
)
def applications_postprocess_POST(request):
    """
    Creates new postprocessing rules for applications
    """
    resource = request.context.resource
    conf = ApplicationPostprocessConf()
    conf.do = "postprocess"
    conf.new_value = "1"
    resource.postprocess_conf.append(conf)
    DBSession.flush()
    return conf.get_dict()


@view_config(
    route_name="applications_property",
    match_param="key=postprocessing_rules",
    renderer="json",
    request_method="PATCH",
    permission="edit",
)
def applications_postprocess_PATCH(request):
    """
    Creates new postprocessing rules for applications
    """
    json_body = request.unsafe_json_body

    schema = build_rule_schema(json_body["rule"], REPORT_TYPE_MATRIX)
    try:
        schema.deserialize(json_body["rule"])
    except colander.Invalid as exc:
        return HTTPUnprocessableEntity(body=json.dumps(exc.asdict()))

    resource = request.context.resource
    conf = ApplicationPostprocessConfService.by_pkey_and_resource_id(
        json_body["pkey"], resource.resource_id
    )
    conf.rule = request.unsafe_json_body["rule"]
    # for now hardcode int since we dont support anything else so far
    conf.new_value = int(request.unsafe_json_body["new_value"])
    return conf.get_dict()


@view_config(
    route_name="applications_property",
    match_param="key=postprocessing_rules",
    renderer="json",
    request_method="DELETE",
    permission="edit",
)
def applications_postprocess_DELETE(request):
    """
    Removes application postprocessing rules
    """
    form = forms.ReactorForm(request.POST, csrf_context=request)
    resource = request.context.resource
    if form.validate():
        for postprocess_conf in resource.postprocess_conf:
            if postprocess_conf.pkey == int(request.GET["pkey"]):
                # remove rule
                DBSession.delete(postprocess_conf)
    return True


@view_config(
    route_name="applications_property",
    match_param="key=report_graphs",
    renderer="json",
    permission="view",
)
@view_config(
    route_name="applications_property",
    match_param="key=slow_report_graphs",
    renderer="json",
    permission="view",
)
def get_application_report_stats(request):
    query_params = request.GET.mixed()
    query_params["resource"] = (request.context.resource.resource_id,)

    filter_settings = build_filter_settings_from_query_dict(request, query_params)
    if not filter_settings.get("end_date"):
        end_date = datetime.utcnow().replace(microsecond=0, second=0)
        filter_settings["end_date"] = end_date

    if not filter_settings.get("start_date"):
        delta = timedelta(hours=1)
        filter_settings["start_date"] = filter_settings["end_date"] - delta

    result = ReportGroupService.get_report_stats(request, filter_settings)
    return result


@view_config(
    route_name="applications_property",
    match_param="key=metrics_graphs",
    renderer="json",
    permission="view",
)
def metrics_graphs(request):
    """
    Handles metric dashboard graphs
    Returns information for time/tier breakdown
    """
    query_params = request.GET.mixed()
    query_params["resource"] = (request.context.resource.resource_id,)

    filter_settings = build_filter_settings_from_query_dict(request, query_params)

    if not filter_settings.get("end_date"):
        end_date = datetime.utcnow().replace(microsecond=0, second=0)
        filter_settings["end_date"] = end_date

    delta = timedelta(hours=1)
    if not filter_settings.get("start_date"):
        filter_settings["start_date"] = filter_settings["end_date"] - delta
    if filter_settings["end_date"] <= filter_settings["start_date"]:
        filter_settings["end_date"] = filter_settings["start_date"]

    delta = filter_settings["end_date"] - filter_settings["start_date"]
    if delta < h.time_deltas.get("12h")["delta"]:
        divide_by_min = 1
    elif delta <= h.time_deltas.get("3d")["delta"]:
        divide_by_min = 5.0
    elif delta >= h.time_deltas.get("2w")["delta"]:
        divide_by_min = 60.0 * 24
    else:
        divide_by_min = 60.0

    results = RequestMetricService.get_metrics_stats(request, filter_settings)
    # because requests are PER SECOND / we divide 1 min stats by 60
    # requests are normalized to 1 min average
    # results are average seconds time spent per request in specific area
    for point in results:
        if point["requests"]:
            point["main"] = (
                point["main"]
                - point["sql"]
                - point["nosql"]
                - point["remote"]
                - point["tmpl"]
                - point["custom"]
            ) / point["requests"]
            point["sql"] = point["sql"] / point["requests"]
            point["nosql"] = point["nosql"] / point["requests"]
            point["remote"] = point["remote"] / point["requests"]
            point["tmpl"] = point["tmpl"] / point["requests"]
            point["custom"] = point["custom"] / point["requests"]
            point["requests_2"] = point["requests"] / 60.0 / divide_by_min

    selected_types = ["main", "sql", "nosql", "remote", "tmpl", "custom"]

    for point in results:
        for stat_type in selected_types:
            point[stat_type] = round(point.get(stat_type, 0), 3)

    return results


@view_config(
    route_name="applications_property",
    match_param="key=response_graphs",
    renderer="json",
    permission="view",
)
def response_graphs(request):
    """
    Handles dashboard infomation for avg. response time split by today,
    2 days ago and week ago
    """
    query_params = request.GET.mixed()
    query_params["resource"] = (request.context.resource.resource_id,)

    filter_settings = build_filter_settings_from_query_dict(request, query_params)

    if not filter_settings.get("end_date"):
        end_date = datetime.utcnow().replace(microsecond=0, second=0)
        filter_settings["end_date"] = end_date

    delta = timedelta(hours=1)
    if not filter_settings.get("start_date"):
        filter_settings["start_date"] = filter_settings["end_date"] - delta

    result_now = RequestMetricService.get_metrics_stats(request, filter_settings)

    filter_settings_2d = filter_settings.copy()
    filter_settings_2d["start_date"] = filter_settings["start_date"] - timedelta(days=2)
    filter_settings_2d["end_date"] = filter_settings["end_date"] - timedelta(days=2)
    result_2d = RequestMetricService.get_metrics_stats(request, filter_settings_2d)

    filter_settings_7d = filter_settings.copy()
    filter_settings_7d["start_date"] = filter_settings["start_date"] - timedelta(days=7)
    filter_settings_7d["end_date"] = filter_settings["end_date"] - timedelta(days=7)
    result_7d = RequestMetricService.get_metrics_stats(request, filter_settings_7d)

    plot_data = []

    for item in result_now:
        point = {"x": item["x"], "today": 0, "days_ago_2": 0, "days_ago_7": 0}
        if item["requests"]:
            point["today"] = round(item["main"] / item["requests"], 3)
        plot_data.append(point)

    for i, item in enumerate(result_2d[: len(plot_data)]):
        plot_data[i]["days_ago_2"] = 0
        point = result_2d[i]
        if point["requests"]:
            plot_data[i]["days_ago_2"] = round(point["main"] / point["requests"], 3)

    for i, item in enumerate(result_7d[: len(plot_data)]):
        plot_data[i]["days_ago_7"] = 0
        point = result_7d[i]
        if point["requests"]:
            plot_data[i]["days_ago_7"] = round(point["main"] / point["requests"], 3)

    return plot_data


@view_config(
    route_name="applications_property",
    match_param="key=requests_graphs",
    renderer="json",
    permission="view",
)
def requests_graphs(request):
    """
    Handles dashboard infomation for avg. response time split by today,
    2 days ago and week ago
    """
    query_params = request.GET.mixed()
    query_params["resource"] = (request.context.resource.resource_id,)

    filter_settings = build_filter_settings_from_query_dict(request, query_params)

    if not filter_settings.get("end_date"):
        end_date = datetime.utcnow().replace(microsecond=0, second=0)
        filter_settings["end_date"] = end_date

    delta = timedelta(hours=1)
    if not filter_settings.get("start_date"):
        filter_settings["start_date"] = filter_settings["end_date"] - delta

    result_now = RequestMetricService.get_metrics_stats(request, filter_settings)

    delta = filter_settings["end_date"] - filter_settings["start_date"]
    if delta < h.time_deltas.get("12h")["delta"]:
        seconds = h.time_deltas["1m"]["minutes"] * 60.0
    elif delta <= h.time_deltas.get("3d")["delta"]:
        seconds = h.time_deltas["5m"]["minutes"] * 60.0
    elif delta >= h.time_deltas.get("2w")["delta"]:
        seconds = h.time_deltas["24h"]["minutes"] * 60.0
    else:
        seconds = h.time_deltas["1h"]["minutes"] * 60.0

    for item in result_now:
        if item["requests"]:
            item["requests"] = round(item["requests"] / seconds, 3)
    return result_now


@view_config(
    route_name="applications_property",
    match_param="key=apdex_stats",
    renderer="json",
    permission="view",
)
def get_apdex_stats(request):
    """
    Returns information and calculates APDEX score per server for dashboard
    server information (upper right stats boxes)
    """
    query_params = request.GET.mixed()
    query_params["resource"] = (request.context.resource.resource_id,)

    filter_settings = build_filter_settings_from_query_dict(request, query_params)
    # make sure we have only one resource here to don't produce
    # weird results when we have wrong app in app selector
    filter_settings["resource"] = [filter_settings["resource"][0]]

    if not filter_settings.get("end_date"):
        end_date = datetime.utcnow().replace(microsecond=0, second=0)
        filter_settings["end_date"] = end_date

    delta = timedelta(hours=1)
    if not filter_settings.get("start_date"):
        filter_settings["start_date"] = filter_settings["end_date"] - delta

    return RequestMetricService.get_apdex_stats(request, filter_settings)


@view_config(
    route_name="applications_property",
    match_param="key=slow_calls",
    renderer="json",
    permission="view",
)
def get_slow_calls(request):
    """
    Returns information for time consuming calls in specific time interval
    """
    query_params = request.GET.mixed()
    query_params["resource"] = (request.context.resource.resource_id,)

    filter_settings = build_filter_settings_from_query_dict(request, query_params)

    if not filter_settings.get("end_date"):
        end_date = datetime.utcnow().replace(microsecond=0, second=0)
        filter_settings["end_date"] = end_date

    delta = timedelta(hours=1)
    if not filter_settings.get("start_date"):
        filter_settings["start_date"] = filter_settings["end_date"] - delta

    return SlowCallService.get_time_consuming_calls(request, filter_settings)


@view_config(
    route_name="applications_property",
    match_param="key=requests_breakdown",
    renderer="json",
    permission="view",
)
def get_requests_breakdown(request):
    """
    Used on dashboard to get information which views are most used in
    a time interval
    """
    query_params = request.GET.mixed()
    query_params["resource"] = (request.context.resource.resource_id,)

    filter_settings = build_filter_settings_from_query_dict(request, query_params)
    if not filter_settings.get("end_date"):
        end_date = datetime.utcnow().replace(microsecond=0, second=0)
        filter_settings["end_date"] = end_date

    if not filter_settings.get("start_date"):
        delta = timedelta(hours=1)
        filter_settings["start_date"] = filter_settings["end_date"] - delta

    series = RequestMetricService.get_requests_breakdown(request, filter_settings)

    results = []
    for row in series:
        d_row = {
            "avg_response": round(row["main"] / row["requests"], 3),
            "requests": row["requests"],
            "main": row["main"],
            "view_name": row["key"],
            "latest_details": row["latest_details"],
            "percentage": round(row["percentage"] * 100, 1),
        }

        results.append(d_row)

    return results


@view_config(
    route_name="applications_property",
    match_param="key=trending_reports",
    renderer="json",
    permission="view",
)
def trending_reports(request):
    """
    Returns exception/slow reports trending for specific time interval
    """
    query_params = request.GET.mixed().copy()
    # pop report type to rewrite it to tag later
    report_type = query_params.pop("report_type", None)
    if report_type:
        query_params["type"] = report_type

    query_params["resource"] = (request.context.resource.resource_id,)

    filter_settings = build_filter_settings_from_query_dict(request, query_params)

    if not filter_settings.get("end_date"):
        end_date = datetime.utcnow().replace(microsecond=0, second=0)
        filter_settings["end_date"] = end_date

    if not filter_settings.get("start_date"):
        delta = timedelta(hours=1)
        filter_settings["start_date"] = filter_settings["end_date"] - delta

    results = ReportGroupService.get_trending(request, filter_settings)

    trending = []
    for occurences, group in results:
        report_group = group.get_dict(request)
        # show the occurences in time range instead of global ones
        report_group["occurences"] = occurences
        trending.append(report_group)

    return trending


@view_config(
    route_name="applications_property",
    match_param="key=integrations",
    renderer="json",
    permission="view",
)
def integrations(request):
    """
    Integration list for given application
    """
    application = request.context.resource
    return {"resource": application}


@view_config(
    route_name="applications_property",
    match_param="key=user_permissions",
    renderer="json",
    permission="owner",
    request_method="POST",
)
def user_resource_permission_create(request):
    """
    Set new permissions for user for a resource
    """
    resource = request.context.resource
    user_name = request.unsafe_json_body.get("user_name")
    user = UserService.by_user_name(user_name)
    if not user:
        user = UserService.by_email(user_name)
    if not user:
        return False

    for perm_name in request.unsafe_json_body.get("permissions", []):
        permission = UserResourcePermissionService.by_resource_user_and_perm(
            user.id, perm_name, resource.resource_id
        )
        if not permission:
            permission = UserResourcePermission(perm_name=perm_name, user_id=user.id)
            resource.user_permissions.append(permission)
    DBSession.flush()
    perms = [
        p.perm_name
        for p in ResourceService.perms_for_user(resource, user)
        if p.type == "user"
    ]
    result = {"user_name": user.user_name, "permissions": list(set(perms))}
    return result


@view_config(
    route_name="applications_property",
    match_param="key=user_permissions",
    renderer="json",
    permission="owner",
    request_method="DELETE",
)
def user_resource_permission_delete(request):
    """
    Removes user permission from specific resource
    """
    resource = request.context.resource

    user = UserService.by_user_name(request.GET.get("user_name"))
    if not user:
        return False

    for perm_name in request.GET.getall("permissions"):
        permission = UserResourcePermissionService.by_resource_user_and_perm(
            user.id, perm_name, resource.resource_id
        )
        resource.user_permissions.remove(permission)
    DBSession.flush()
    perms = [
        p.perm_name
        for p in ResourceService.perms_for_user(resource, user)
        if p.type == "user"
    ]
    result = {"user_name": user.user_name, "permissions": list(set(perms))}
    return result


@view_config(
    route_name="applications_property",
    match_param="key=group_permissions",
    renderer="json",
    permission="owner",
    request_method="POST",
)
def group_resource_permission_create(request):
    """
    Set new permissions for group for a resource
    """
    resource = request.context.resource
    group = GroupService.by_id(request.unsafe_json_body.get("group_id"))
    if not group:
        return False

    for perm_name in request.unsafe_json_body.get("permissions", []):
        permission = GroupResourcePermissionService.by_resource_group_and_perm(
            group.id, perm_name, resource.resource_id
        )
        if not permission:
            permission = GroupResourcePermission(perm_name=perm_name, group_id=group.id)
            resource.group_permissions.append(permission)
    DBSession.flush()
    perm_tuples = ResourceService.groups_for_perm(
        resource, ANY_PERMISSION, limit_group_permissions=True, group_ids=[group.id]
    )
    perms = [p.perm_name for p in perm_tuples if p.type == "group"]
    result = {"group": group.get_dict(), "permissions": list(set(perms))}
    return result


@view_config(
    route_name="applications_property",
    match_param="key=group_permissions",
    renderer="json",
    permission="owner",
    request_method="DELETE",
)
def group_resource_permission_delete(request):
    """
    Removes group permission from specific resource
    """
    form = forms.ReactorForm(request.POST, csrf_context=request)
    form.validate()
    resource = request.context.resource
    group = GroupService.by_id(request.GET.get("group_id"))
    if not group:
        return False

    for perm_name in request.GET.getall("permissions"):
        permission = GroupResourcePermissionService.by_resource_group_and_perm(
            group.id, perm_name, resource.resource_id
        )
        resource.group_permissions.remove(permission)
    DBSession.flush()
    perm_tuples = ResourceService.groups_for_perm(
        resource, ANY_PERMISSION, limit_group_permissions=True, group_ids=[group.id]
    )
    perms = [p.perm_name for p in perm_tuples if p.type == "group"]
    result = {"group": group.get_dict(), "permissions": list(set(perms))}
    return result
