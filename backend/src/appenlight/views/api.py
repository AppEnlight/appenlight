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

import base64
import io
import datetime
import json
import logging
import urllib.request, urllib.parse, urllib.error
import zlib

from gzip import GzipFile
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPBadRequest

import appenlight.celery.tasks as tasks
from appenlight.lib.api import rate_limiting, check_cors
from appenlight.lib.enums import ParsedSentryEventType
from appenlight.lib.utils import parse_proto
from appenlight.lib.utils.airbrake import parse_airbrake_xml
from appenlight.lib.utils.date_utils import convert_date
from appenlight.lib.utils.sentry import parse_sentry_event
from appenlight.lib.request import JSONException
from appenlight.validators import (
    LogListSchema,
    MetricsListSchema,
    GeneralMetricsListSchema,
    GeneralMetricsPermanentListSchema,
    GeneralMetricSchema,
    GeneralMetricPermanentSchema,
    LogListPermanentSchema,
    ReportListSchema_0_5,
    LogSchema,
    LogSchemaPermanent,
    ReportSchema_0_5,
)

log = logging.getLogger(__name__)


@view_config(
    route_name="api_logs", renderer="string", permission="create", require_csrf=False
)
@view_config(
    route_name="api_log", renderer="string", permission="create", require_csrf=False
)
def logs_create(request):
    """
    Endpoint for log aggregation
    """
    application = request.context.resource
    if request.method.upper() == "OPTIONS":
        return check_cors(request, application)
    else:
        check_cors(request, application, should_return=False)

    params = dict(request.params.copy())
    proto_version = parse_proto(params.get("protocol_version", ""))
    payload = request.unsafe_json_body
    sequence_accepted = request.matched_route.name == "api_logs"

    if sequence_accepted:
        if application.allow_permanent_storage:
            schema = LogListPermanentSchema().bind(utcnow=datetime.datetime.utcnow())
        else:
            schema = LogListSchema().bind(utcnow=datetime.datetime.utcnow())
    else:
        if application.allow_permanent_storage:
            schema = LogSchemaPermanent().bind(utcnow=datetime.datetime.utcnow())
        else:
            schema = LogSchema().bind(utcnow=datetime.datetime.utcnow())

    deserialized_logs = schema.deserialize(payload)
    if sequence_accepted is False:
        deserialized_logs = [deserialized_logs]

    rate_limiting(
        request, application, "per_application_logs_rate_limit", len(deserialized_logs)
    )

    # pprint.pprint(deserialized_logs)

    # we need to split those out so we can process the pkey ones one by one
    non_pkey_logs = [
        log_dict for log_dict in deserialized_logs if not log_dict["primary_key"]
    ]
    pkey_dict = {}
    # try to process the logs as best as we can and group together to reduce
    # the amount of
    for log_dict in deserialized_logs:
        if log_dict["primary_key"]:
            key = (log_dict["primary_key"], log_dict["namespace"])
            if not key in pkey_dict:
                pkey_dict[key] = []
            pkey_dict[key].append(log_dict)

    if non_pkey_logs:
        log.debug("%s non-pkey logs received: %s" % (application, len(non_pkey_logs)))
        tasks.add_logs.delay(application.resource_id, params, non_pkey_logs)
    if pkey_dict:
        logs_to_insert = []
        for primary_key_tuple, payload in pkey_dict.items():
            sorted_logs = sorted(payload, key=lambda x: x["date"])
            logs_to_insert.append(sorted_logs[-1])
        log.debug("%s pkey logs received: %s" % (application, len(logs_to_insert)))
        tasks.add_logs.delay(application.resource_id, params, logs_to_insert)

    log.info(
        "LOG call %s %s client:%s"
        % (application, proto_version, request.headers.get("user_agent"))
    )
    return "OK: Logs accepted"


@view_config(
    route_name="api_request_stats",
    renderer="string",
    permission="create",
    require_csrf=False,
)
@view_config(
    route_name="api_metrics", renderer="string", permission="create", require_csrf=False
)
def request_metrics_create(request):
    """
    Endpoint for performance metrics, aggregates view performance stats
    and converts them to general metric row
    """
    application = request.context.resource
    if request.method.upper() == "OPTIONS":
        return check_cors(request, application)
    else:
        check_cors(request, application, should_return=False)

    params = dict(request.params.copy())
    proto_version = parse_proto(params.get("protocol_version", ""))

    payload = request.unsafe_json_body
    schema = MetricsListSchema()
    dataset = schema.deserialize(payload)

    rate_limiting(
        request, application, "per_application_metrics_rate_limit", len(dataset)
    )

    # looping report data
    metrics = {}
    for metric in dataset:
        server_name = metric.get("server", "").lower() or "unknown"
        start_interval = convert_date(metric["timestamp"])
        start_interval = start_interval.replace(second=0, microsecond=0)

        for view_name, view_metrics in metric["metrics"]:
            key = "%s%s%s" % (metric["server"], start_interval, view_name)
            if start_interval not in metrics:
                metrics[key] = {
                    "requests": 0,
                    "main": 0,
                    "sql": 0,
                    "nosql": 0,
                    "remote": 0,
                    "tmpl": 0,
                    "custom": 0,
                    "sql_calls": 0,
                    "nosql_calls": 0,
                    "remote_calls": 0,
                    "tmpl_calls": 0,
                    "custom_calls": 0,
                    "start_interval": start_interval,
                    "server_name": server_name,
                    "view_name": view_name,
                }
            metrics[key]["requests"] += int(view_metrics["requests"])
            metrics[key]["main"] += round(view_metrics["main"], 5)
            metrics[key]["sql"] += round(view_metrics["sql"], 5)
            metrics[key]["nosql"] += round(view_metrics["nosql"], 5)
            metrics[key]["remote"] += round(view_metrics["remote"], 5)
            metrics[key]["tmpl"] += round(view_metrics["tmpl"], 5)
            metrics[key]["custom"] += round(view_metrics.get("custom", 0.0), 5)
            metrics[key]["sql_calls"] += int(view_metrics.get("sql_calls", 0))
            metrics[key]["nosql_calls"] += int(view_metrics.get("nosql_calls", 0))
            metrics[key]["remote_calls"] += int(view_metrics.get("remote_calls", 0))
            metrics[key]["tmpl_calls"] += int(view_metrics.get("tmpl_calls", 0))
            metrics[key]["custom_calls"] += int(view_metrics.get("custom_calls", 0))

            if not metrics[key]["requests"]:
                # fix this here because validator can't
                metrics[key]["requests"] = 1
                # metrics dict is being built to minimize
                # the amount of queries used
                # in case we get multiple rows from same minute

    normalized_metrics = []
    for metric in metrics.values():
        new_metric = {
            "namespace": "appenlight.request_metric",
            "timestamp": metric.pop("start_interval"),
            "server_name": metric["server_name"],
            "tags": list(metric.items()),
        }
        normalized_metrics.append(new_metric)

    tasks.add_metrics.delay(
        application.resource_id, params, normalized_metrics, proto_version
    )

    log.info(
        "REQUEST METRICS call {} {} client:{}".format(
            application.resource_name, proto_version, request.headers.get("user_agent")
        )
    )
    return "OK: request metrics accepted"


@view_config(
    route_name="api_general_metrics",
    renderer="string",
    permission="create",
    require_csrf=False,
)
@view_config(
    route_name="api_general_metric",
    renderer="string",
    permission="create",
    require_csrf=False,
)
def general_metrics_create(request):
    """
    Endpoint for general metrics aggregation
    """
    application = request.context.resource
    if request.method.upper() == "OPTIONS":
        return check_cors(request, application)
    else:
        check_cors(request, application, should_return=False)

    params = dict(request.params.copy())
    proto_version = parse_proto(params.get("protocol_version", ""))
    payload = request.unsafe_json_body
    sequence_accepted = request.matched_route.name == "api_general_metrics"
    if sequence_accepted:
        if application.allow_permanent_storage:
            schema = GeneralMetricsPermanentListSchema().bind(
                utcnow=datetime.datetime.utcnow()
            )
        else:
            schema = GeneralMetricsListSchema().bind(utcnow=datetime.datetime.utcnow())
    else:
        if application.allow_permanent_storage:
            schema = GeneralMetricPermanentSchema().bind(
                utcnow=datetime.datetime.utcnow()
            )
        else:
            schema = GeneralMetricSchema().bind(utcnow=datetime.datetime.utcnow())

    deserialized_metrics = schema.deserialize(payload)
    if sequence_accepted is False:
        deserialized_metrics = [deserialized_metrics]

    rate_limiting(
        request,
        application,
        "per_application_metrics_rate_limit",
        len(deserialized_metrics),
    )

    tasks.add_metrics.delay(
        application.resource_id, params, deserialized_metrics, proto_version
    )

    log.info(
        "METRICS call {} {} client:{}".format(
            application.resource_name, proto_version, request.headers.get("user_agent")
        )
    )
    return "OK: Metrics accepted"


@view_config(
    route_name="api_reports", renderer="string", permission="create", require_csrf=False
)
@view_config(
    route_name="api_slow_reports",
    renderer="string",
    permission="create",
    require_csrf=False,
)
@view_config(
    route_name="api_report", renderer="string", permission="create", require_csrf=False
)
def reports_create(request):
    """
    Endpoint for exception and slowness reports
    """
    # route_url('reports')
    application = request.context.resource
    if request.method.upper() == "OPTIONS":
        return check_cors(request, application)
    else:
        check_cors(request, application, should_return=False)
    params = dict(request.params.copy())
    proto_version = parse_proto(params.get("protocol_version", ""))
    payload = request.unsafe_json_body
    sequence_accepted = request.matched_route.name == "api_reports"

    if sequence_accepted:
        schema = ReportListSchema_0_5().bind(utcnow=datetime.datetime.utcnow())
    else:
        schema = ReportSchema_0_5().bind(utcnow=datetime.datetime.utcnow())

    deserialized_reports = schema.deserialize(payload)
    if sequence_accepted is False:
        deserialized_reports = [deserialized_reports]
    if deserialized_reports:
        rate_limiting(
            request,
            application,
            "per_application_reports_rate_limit",
            len(deserialized_reports),
        )

        # pprint.pprint(deserialized_reports)
        tasks.add_reports.delay(application.resource_id, params, deserialized_reports)
    log.info(
        "REPORT call  %s, %s client:%s"
        % (application, proto_version, request.headers.get("user_agent"))
    )
    return "OK: Reports accepted"


@view_config(
    route_name="api_airbrake",
    renderer="string",
    permission="create",
    require_csrf=False,
)
def airbrake_xml_compat(request):
    """
    Airbrake compatible endpoint for XML reports
    """
    application = request.context.resource
    if request.method.upper() == "OPTIONS":
        return check_cors(request, application)
    else:
        check_cors(request, application, should_return=False)

    params = dict(request.params.copy())

    error_dict = parse_airbrake_xml(request)
    schema = ReportListSchema_0_5().bind(utcnow=datetime.datetime.utcnow())
    deserialized_reports = schema.deserialize([error_dict])
    rate_limiting(
        request,
        application,
        "per_application_reports_rate_limit",
        len(deserialized_reports),
    )

    tasks.add_reports.delay(application.resource_id, params, deserialized_reports)
    log.info(
        "%s AIRBRAKE call for application %s, api_ver:%s client:%s"
        % (
            500,
            application.resource_name,
            request.params.get("protocol_version", "unknown"),
            request.headers.get("user_agent"),
        )
    )
    return (
        "<notice><id>no-id</id><url>%s</url></notice>"
        % request.registry.settings["mailing.app_url"]
    )


def decompress_gzip(data):
    try:
        fp = io.StringIO(data)
        with GzipFile(fileobj=fp) as f:
            return f.read()
    except Exception as exc:
        raise
        log.error(exc)
        raise HTTPBadRequest()


def decompress_zlib(data):
    try:
        return zlib.decompress(data)
    except Exception as exc:
        raise
        log.error(exc)
        raise HTTPBadRequest()


def decode_b64(data):
    try:
        return base64.b64decode(data)
    except Exception as exc:
        raise
        log.error(exc)
        raise HTTPBadRequest()


@view_config(
    route_name="api_sentry", renderer="string", permission="create", require_csrf=False
)
@view_config(
    route_name="api_sentry_slash",
    renderer="string",
    permission="create",
    require_csrf=False,
)
def sentry_compat(request):
    """
    Sentry compatible endpoint
    """
    application = request.context.resource
    if request.method.upper() == "OPTIONS":
        return check_cors(request, application)
    else:
        check_cors(request, application, should_return=False)

    # handle various report encoding
    content_encoding = request.headers.get("Content-Encoding")
    content_type = request.headers.get("Content-Type")
    if content_encoding == "gzip":
        body = decompress_gzip(request.body)
    elif content_encoding == "deflate":
        body = decompress_zlib(request.body)
    else:
        body = request.body
        # attempt to fix string before decoding for stupid clients
        if content_type == "application/x-www-form-urlencoded":
            body = urllib.parse.unquote(body.decode("utf8"))
        check_char = "{" if isinstance(body, str) else b"{"
        if not body.startswith(check_char):
            try:
                body = decode_b64(body)
                body = decompress_zlib(body)
            except Exception as exc:
                log.info(exc)

    try:
        json_body = json.loads(body.decode("utf8"))
    except ValueError:
        raise JSONException("Incorrect JSON")

    event, event_type = parse_sentry_event(json_body)

    if event_type == ParsedSentryEventType.LOG:
        if application.allow_permanent_storage:
            schema = LogSchemaPermanent().bind(utcnow=datetime.datetime.utcnow())
        else:
            schema = LogSchema().bind(utcnow=datetime.datetime.utcnow())
        deserialized_logs = schema.deserialize(event)
        non_pkey_logs = [deserialized_logs]
        log.debug("%s non-pkey logs received: %s" % (application, len(non_pkey_logs)))
        tasks.add_logs.delay(application.resource_id, {}, non_pkey_logs)
    if event_type == ParsedSentryEventType.ERROR_REPORT:
        schema = ReportSchema_0_5().bind(
            utcnow=datetime.datetime.utcnow(),
            allow_permanent_storage=application.allow_permanent_storage,
        )
        deserialized_reports = [schema.deserialize(event)]
        rate_limiting(
            request,
            application,
            "per_application_reports_rate_limit",
            len(deserialized_reports),
        )
        tasks.add_reports.delay(application.resource_id, {}, deserialized_reports)
    return "OK: Events accepted"
