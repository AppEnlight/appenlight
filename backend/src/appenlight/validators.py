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

import datetime

import colander
from colander import null

# those keywords are here so we can distingush between searching for tags and
# normal properties of reports/logs
accepted_search_params = ['resource',
                          'request_id',
                          'start_date',
                          'end_date',
                          'page',
                          'min_occurences',
                          'http_status',
                          'priority',
                          'error',
                          'url_path',
                          'url_domain',
                          'report_status',
                          'min_duration',
                          'max_duration',
                          'message',
                          'level',
                          'namespace']


@colander.deferred
def deferred_utcnow(node, kw):
    return kw['utcnow']


@colander.deferred
def optional_limited_date(node, kw):
    if not kw.get('allow_permanent_storage'):
        return limited_date


def lowercase_preparer(input_data):
    """
    Transforms a list of string entries to lowercase
    Used in search query validation
    """
    if not input_data:
        return input_data
    return [x.lower() for x in input_data]


def shortener_factory(cutoff_size=32):
    """
    Limits the input data to specific character count
    :arg cutoff_cutoff_size How much characters to store

    """

    def shortener(input_data):
        if not input_data:
            return input_data
        else:
            if isinstance(input_data, str):
                return input_data[:cutoff_size]
            else:
                return input_data

    return shortener


def cast_to_unicode_or_null(value):
    if value is not colander.null:
        return str(value)
    return None


class NonTZDate(colander.DateTime):
    """ Returns null for incorrect date format - also removes tz info"""

    def deserialize(self, node, cstruct):
        # disabled for now
        # if cstruct and isinstance(cstruct, str):
        #     if ':' not in cstruct:
        #         cstruct += ':0.0'
        #     if '.' not in cstruct:
        #         cstruct += '.0'
        value = super(NonTZDate, self).deserialize(node, cstruct)
        if value:
            return value.replace(tzinfo=None)
        return value


class UnknownType(object):
    """
    Universal type that will accept a deserialized JSON object and store it unaltered
    """

    def serialize(self, node, appstruct):
        if appstruct is null:
            return null
        return appstruct

    def deserialize(self, node, cstruct):
        if cstruct is null:
            return null
        return cstruct

    def cstruct_children(self):
        return []


# SLOW REPORT SCHEMA

def rewrite_type(input_data):
    """
    Fix for legacy appenlight clients
    """
    if input_data == 'remote_call':
        return 'remote'
    return input_data


class ExtraTupleSchema(colander.TupleSchema):
    name = colander.SchemaNode(colander.String(),
                               validator=colander.Length(1, 64))
    value = colander.SchemaNode(UnknownType(),
                                preparer=shortener_factory(512),
                                missing=None)


class ExtraSchemaList(colander.SequenceSchema):
    tag = ExtraTupleSchema()
    missing = None


class TagsTupleSchema(colander.TupleSchema):
    name = colander.SchemaNode(colander.String(),
                               validator=colander.Length(1, 128))
    value = colander.SchemaNode(UnknownType(),
                                preparer=shortener_factory(128),
                                missing=None)


class TagSchemaList(colander.SequenceSchema):
    tag = TagsTupleSchema()
    missing = None


class NumericTagsTupleSchema(colander.TupleSchema):
    name = colander.SchemaNode(colander.String(),
                               validator=colander.Length(1, 128))
    value = colander.SchemaNode(colander.Float(), missing=0)


class NumericTagSchemaList(colander.SequenceSchema):
    tag = NumericTagsTupleSchema()
    missing = None


class SlowCallSchema(colander.MappingSchema):
    """
    Validates slow call format in slow call list
    """
    start = colander.SchemaNode(NonTZDate())
    end = colander.SchemaNode(NonTZDate())
    statement = colander.SchemaNode(colander.String(), missing='')
    parameters = colander.SchemaNode(UnknownType(), missing=None)
    type = colander.SchemaNode(
        colander.String(),
        preparer=rewrite_type,
        validator=colander.OneOf(
            ['tmpl', 'sql', 'nosql', 'remote', 'unknown', 'custom']),
        missing='unknown')
    subtype = colander.SchemaNode(colander.String(),
                                  validator=colander.Length(1, 16),
                                  missing='unknown')
    location = colander.SchemaNode(colander.String(),
                                   validator=colander.Length(1, 255),
                                   missing='')


def limited_date(node, value):
    """ checks to make sure that the value is not older/newer than 2h """
    past_hours = 72
    future_hours = 2
    min_time = datetime.datetime.utcnow() - datetime.timedelta(
        hours=past_hours)
    max_time = datetime.datetime.utcnow() + datetime.timedelta(
        hours=future_hours)
    if min_time > value:
        msg = '%r is older from current UTC time by ' + str(past_hours)
        msg += ' hours. Ask administrator to enable permanent logging for ' \
               'your application to store logs with dates in past.'
        raise colander.Invalid(node, msg % value)
    if max_time < value:
        msg = '%r is newer from current UTC time by ' + str(future_hours)
        msg += ' hours. Ask administrator to enable permanent logging for ' \
               'your application to store logs with dates in future.'
        raise colander.Invalid(node, msg % value)


class SlowCallListSchema(colander.SequenceSchema):
    """
    Validates list of individual slow calls
    """
    slow_call = SlowCallSchema()


class RequestStatsSchema(colander.MappingSchema):
    """
    Validates format of requests statistics dictionary
    """
    main = colander.SchemaNode(colander.Float(), validator=colander.Range(0),
                               missing=0)
    sql = colander.SchemaNode(colander.Float(), validator=colander.Range(0),
                              missing=0)
    nosql = colander.SchemaNode(colander.Float(), validator=colander.Range(0),
                                missing=0)
    remote = colander.SchemaNode(colander.Float(), validator=colander.Range(0),
                                 missing=0)
    tmpl = colander.SchemaNode(colander.Float(), validator=colander.Range(0),
                               missing=0)
    custom = colander.SchemaNode(colander.Float(), validator=colander.Range(0),
                                 missing=0)
    sql_calls = colander.SchemaNode(colander.Float(),
                                    validator=colander.Range(0),
                                    missing=0)
    nosql_calls = colander.SchemaNode(colander.Float(),
                                      validator=colander.Range(0),
                                      missing=0)
    remote_calls = colander.SchemaNode(colander.Float(),
                                       validator=colander.Range(0),
                                       missing=0)
    tmpl_calls = colander.SchemaNode(colander.Float(),
                                     validator=colander.Range(0),
                                     missing=0)
    custom_calls = colander.SchemaNode(colander.Float(),
                                       validator=colander.Range(0),
                                       missing=0)


class FrameInfoVarSchema(colander.SequenceSchema):
    """
    Validates format of frame variables of a traceback
    """
    vars = colander.SchemaNode(UnknownType(),
                               validator=colander.Length(2, 2))


class FrameInfoSchema(colander.MappingSchema):
    """
    Validates format of a traceback line
    """
    cline = colander.SchemaNode(colander.String(), missing='')
    module = colander.SchemaNode(colander.String(), missing='')
    line = colander.SchemaNode(colander.String(), missing='')
    file = colander.SchemaNode(colander.String(), missing='')
    fn = colander.SchemaNode(colander.String(), missing='')
    vars = FrameInfoVarSchema()


class FrameInfoListSchema(colander.SequenceSchema):
    """
    Validates format of list of traceback lines
    """
    frame = colander.SchemaNode(UnknownType())


class ReportDetailBaseSchema(colander.MappingSchema):
    """
    Validates format of report - ie. request parameters and stats for a request in report group
    """
    username = colander.SchemaNode(colander.String(),
                                   preparer=[shortener_factory(255),
                                             lambda x: x or ''],
                                   missing='')
    request_id = colander.SchemaNode(colander.String(),
                                     preparer=shortener_factory(40),
                                     missing='')
    url = colander.SchemaNode(colander.String(),
                              preparer=shortener_factory(1024), missing='')
    ip = colander.SchemaNode(colander.String(), preparer=shortener_factory(39),
                             missing=None)
    start_time = colander.SchemaNode(NonTZDate(),
                                     validator=optional_limited_date,
                                     missing=deferred_utcnow)
    end_time = colander.SchemaNode(NonTZDate(),
                                   validator=optional_limited_date,
                                   missing=None)
    user_agent = colander.SchemaNode(colander.String(),
                                     preparer=[shortener_factory(512),
                                               lambda x: x or ''],
                                     missing='')
    message = colander.SchemaNode(colander.String(),
                                  preparer=shortener_factory(2048),
                                  missing='')
    group_string = colander.SchemaNode(colander.String(),
                                       validator=colander.Length(1, 512),
                                       missing=None)
    request_stats = RequestStatsSchema(missing=None)
    request = colander.SchemaNode(colander.Mapping(unknown='preserve'),
                                  missing={})
    traceback = FrameInfoListSchema(missing=None)
    slow_calls = SlowCallListSchema(missing=[])
    extra = ExtraSchemaList()


class ReportDetailSchema_0_5(ReportDetailBaseSchema):
    pass


class ReportDetailSchemaPermissiveDate_0_5(ReportDetailSchema_0_5):
    start_time = colander.SchemaNode(NonTZDate(), missing=deferred_utcnow)
    end_time = colander.SchemaNode(NonTZDate(), missing=None)


class ReportSchemaBase(colander.MappingSchema):
    """
    Validates format of report group
    """
    client = colander.SchemaNode(colander.String(),
                                 preparer=lambda x: x or 'unknown')
    server = colander.SchemaNode(
        colander.String(),
        preparer=[
            lambda x: x.lower() if x else 'unknown', shortener_factory(128)],
        missing='unknown')
    priority = colander.SchemaNode(colander.Int(),
                                   preparer=[lambda x: x or 5],
                                   validator=colander.Range(1, 10),
                                   missing=5)
    language = colander.SchemaNode(colander.String(), missing='unknown')
    error = colander.SchemaNode(colander.String(),
                                preparer=shortener_factory(512),
                                missing='')
    view_name = colander.SchemaNode(colander.String(),
                                    preparer=[shortener_factory(128),
                                              lambda x: x or ''],
                                    missing='')
    http_status = colander.SchemaNode(colander.Int(),
                                      preparer=[lambda x: x or 200],
                                      validator=colander.Range(1))

    occurences = colander.SchemaNode(colander.Int(),
                                     validator=colander.Range(1, 99999999999),
                                     missing=1)
    tags = TagSchemaList()


class ReportSchema_0_5(ReportSchemaBase, ReportDetailSchema_0_5):
    pass


class ReportSchemaPermissiveDate_0_5(ReportSchemaBase,
                                 ReportDetailSchemaPermissiveDate_0_5):
    pass


class ReportListSchema_0_5(colander.SequenceSchema):
    """
    Validates format of list of report groups
    """
    report = ReportSchema_0_5()
    validator = colander.Length(1)


class ReportListPermissiveDateSchema_0_5(colander.SequenceSchema):
    """
    Validates format of list of report groups
    """
    report = ReportSchemaPermissiveDate_0_5()
    validator = colander.Length(1)


class LogSchema(colander.MappingSchema):
    """
    Validates format if individual log entry
    """
    primary_key = colander.SchemaNode(UnknownType(),
                                      preparer=[cast_to_unicode_or_null,
                                                shortener_factory(128)],
                                      missing=None)
    log_level = colander.SchemaNode(colander.String(),
                                    preparer=shortener_factory(10),
                                    missing='UNKNOWN')
    message = colander.SchemaNode(colander.String(),
                                  preparer=shortener_factory(4096),
                                  missing='')
    namespace = colander.SchemaNode(colander.String(),
                                    preparer=shortener_factory(128),
                                    missing='')
    request_id = colander.SchemaNode(colander.String(),
                                     preparer=shortener_factory(40),
                                     missing='')
    server = colander.SchemaNode(colander.String(),
                                 preparer=shortener_factory(128),
                                 missing='unknown')
    date = colander.SchemaNode(NonTZDate(),
                               validator=limited_date,
                               missing=deferred_utcnow)
    tags = TagSchemaList()


class LogSchemaPermanent(LogSchema):
    date = colander.SchemaNode(NonTZDate(),
                               missing=deferred_utcnow)
    permanent = colander.SchemaNode(colander.Boolean(), missing=False)


class LogListSchema(colander.SequenceSchema):
    """
    Validates format of list of log entries
    """
    log = LogSchema()
    validator = colander.Length(1)


class LogListPermanentSchema(colander.SequenceSchema):
    """
    Validates format of list of log entries
    """
    log = LogSchemaPermanent()
    validator = colander.Length(1)


class ViewRequestStatsSchema(RequestStatsSchema):
    requests = colander.SchemaNode(colander.Integer(),
                                   validator=colander.Range(0),
                                   missing=0)


class ViewMetricTupleSchema(colander.TupleSchema):
    """
    Validates list of views and their corresponding request stats object ie:
    ["dir/module:func",{"custom": 0.0..}]
    """
    view_name = colander.SchemaNode(colander.String(),
                                    preparer=[shortener_factory(128),
                                              lambda x: x or 'unknown'],
                                    missing='unknown')
    metrics = ViewRequestStatsSchema()


class ViewMetricListSchema(colander.SequenceSchema):
    """
    Validates view breakdown stats objects list
    {metrics key of server/time object}
    """
    view_tuple = ViewMetricTupleSchema()
    validator = colander.Length(1)


class ViewMetricSchema(colander.MappingSchema):
    """
    Validates server/timeinterval object, ie:
    {server/time object}

    """
    timestamp = colander.SchemaNode(NonTZDate(),
                                    validator=limited_date,
                                    missing=None)
    server = colander.SchemaNode(colander.String(),
                                 preparer=[shortener_factory(128),
                                           lambda x: x or 'unknown'],
                                 missing='unknown')
    metrics = ViewMetricListSchema()


class GeneralMetricSchema(colander.MappingSchema):
    """
    Validates universal metric schema

    """
    namespace = colander.SchemaNode(colander.String(), missing='',
                                    preparer=shortener_factory(128))

    server_name = colander.SchemaNode(colander.String(),
                                      preparer=[shortener_factory(128),
                                                lambda x: x or 'unknown'],
                                      missing='unknown')
    timestamp = colander.SchemaNode(NonTZDate(), validator=limited_date,
                                    missing=deferred_utcnow)
    tags = TagSchemaList(missing=colander.required)


class GeneralMetricPermanentSchema(GeneralMetricSchema):
    """
    Validates universal metric schema

    """
    timestamp = colander.SchemaNode(NonTZDate(), missing=deferred_utcnow)


class GeneralMetricsListSchema(colander.SequenceSchema):
    metric = GeneralMetricSchema()
    validator = colander.Length(1)


class GeneralMetricsPermanentListSchema(colander.SequenceSchema):
    metric = GeneralMetricPermanentSchema()
    validator = colander.Length(1)


class MetricsListSchema(colander.SequenceSchema):
    """
    Validates list of metrics objects ie:
    [{server/time object}, ] part


    """
    metric = ViewMetricSchema()
    validator = colander.Length(1)


class StringToAppList(object):
    """
    Returns validated list of application ids from user query and
    set of applications user is allowed to look at
    transform string to list containing single integer
    """

    def serialize(self, node, appstruct):
        if appstruct is null:
            return null
        return appstruct

    def deserialize(self, node, cstruct):
        if cstruct is null:
            return null

        apps = set([int(a) for a in node.bindings['resources']])

        if isinstance(cstruct, str):
            cstruct = [cstruct]

        cstruct = [int(a) for a in cstruct]

        valid_apps = list(apps.intersection(set(cstruct)))
        if valid_apps:
            return valid_apps
        return null

    def cstruct_children(self):
        return []


@colander.deferred
def possible_applications_validator(node, kw):
    possible_apps = [int(a) for a in kw['resources']]
    return colander.All(colander.ContainsOnly(possible_apps),
                        colander.Length(1))


@colander.deferred
def possible_applications(node, kw):
    return [int(a) for a in kw['resources']]


@colander.deferred
def today_start(node, kw):
    return datetime.datetime.utcnow().replace(second=0, microsecond=0,
                                              minute=0,
                                              hour=0)


@colander.deferred
def today_end(node, kw):
    return datetime.datetime.utcnow().replace(second=0, microsecond=0,
                                              minute=59, hour=23)


@colander.deferred
def old_start(node, kw):
    t_delta = datetime.timedelta(days=90)
    return datetime.datetime.utcnow().replace(second=0, microsecond=0,
                                              minute=0,
                                              hour=0) - t_delta


@colander.deferred
def today_end(node, kw):
    return datetime.datetime.utcnow().replace(second=0, microsecond=0,
                                              minute=59, hour=23)


class PermissiveDate(colander.DateTime):
    """ Returns null for incorrect date format - also removes tz info"""

    def deserialize(self, node, cstruct):
        if not cstruct:
            return null

        try:
            result = colander.iso8601.parse_date(
                cstruct, default_timezone=self.default_tzinfo)
        except colander.iso8601.ParseError:
            return null
        return result.replace(tzinfo=None)


class LogSearchSchema(colander.MappingSchema):
    def schema_type(self, **kw):
        return colander.Mapping(unknown='preserve')

    resource = colander.SchemaNode(StringToAppList(),
                                   validator=possible_applications_validator,
                                   missing=possible_applications)

    message = colander.SchemaNode(colander.Sequence(accept_scalar=True),
                                  colander.SchemaNode(colander.String()),
                                  missing=None)
    level = colander.SchemaNode(colander.Sequence(accept_scalar=True),
                                colander.SchemaNode(colander.String()),
                                preparer=lowercase_preparer,
                                missing=None)
    namespace = colander.SchemaNode(colander.Sequence(accept_scalar=True),
                                    colander.SchemaNode(colander.String()),
                                    preparer=lowercase_preparer,
                                    missing=None)
    request_id = colander.SchemaNode(colander.Sequence(accept_scalar=True),
                                     colander.SchemaNode(colander.String()),
                                     preparer=lowercase_preparer,
                                     missing=None)
    start_date = colander.SchemaNode(PermissiveDate(),
                                     missing=None)
    end_date = colander.SchemaNode(PermissiveDate(),
                                   missing=None)
    page = colander.SchemaNode(colander.Integer(),
                               validator=colander.Range(min=1),
                               missing=1)


class ReportSearchSchema(colander.MappingSchema):
    def schema_type(self, **kw):
        return colander.Mapping(unknown='preserve')

    resource = colander.SchemaNode(StringToAppList(),
                                   validator=possible_applications_validator,
                                   missing=possible_applications)
    request_id = colander.SchemaNode(colander.Sequence(accept_scalar=True),
                                     colander.SchemaNode(colander.String()),
                                     missing=None)
    start_date = colander.SchemaNode(PermissiveDate(),
                                     missing=None)
    end_date = colander.SchemaNode(PermissiveDate(),
                                   missing=None)
    page = colander.SchemaNode(colander.Integer(),
                               validator=colander.Range(min=1),
                               missing=1)

    min_occurences = colander.SchemaNode(
        colander.Sequence(accept_scalar=True),
        colander.SchemaNode(colander.Integer()),
        missing=None)

    http_status = colander.SchemaNode(colander.Sequence(accept_scalar=True),
                                      colander.SchemaNode(colander.Integer()),
                                      missing=None)
    priority = colander.SchemaNode(colander.Sequence(accept_scalar=True),
                                   colander.SchemaNode(colander.Integer()),
                                   missing=None)
    error = colander.SchemaNode(colander.Sequence(accept_scalar=True),
                                colander.SchemaNode(colander.String()),
                                missing=None)
    url_path = colander.SchemaNode(colander.Sequence(accept_scalar=True),
                                   colander.SchemaNode(colander.String()),
                                   missing=None)
    url_domain = colander.SchemaNode(colander.Sequence(accept_scalar=True),
                                     colander.SchemaNode(colander.String()),
                                     missing=None)
    report_status = colander.SchemaNode(colander.Sequence(accept_scalar=True),
                                        colander.SchemaNode(colander.String()),
                                        missing=None)
    min_duration = colander.SchemaNode(colander.Sequence(accept_scalar=True),
                                       colander.SchemaNode(colander.Float()),
                                       missing=None)
    max_duration = colander.SchemaNode(colander.Sequence(accept_scalar=True),
                                       colander.SchemaNode(colander.Float()),
                                       missing=None)


class TagSchema(colander.MappingSchema):
    """
    Used in log search
    """
    name = colander.SchemaNode(colander.String(),
                               validator=colander.Length(1, 32))
    value = colander.SchemaNode(colander.Sequence(accept_scalar=True),
                                colander.SchemaNode(colander.String(),
                                                    validator=colander.Length(
                                                        1, 128)),
                                missing=None)
    op = colander.SchemaNode(colander.String(),
                             validator=colander.Length(1, 128),
                             missing=None)


class TagListSchema(colander.SequenceSchema):
    tag = TagSchema()


class RuleFieldType(object):
    """ Validator which succeeds if the value passed to it is one of
    a fixed set of values """

    def __init__(self, cast_to):
        self.cast_to = cast_to

    def __call__(self, node, value):
        try:
            if self.cast_to == 'int':
                int(value)
            elif self.cast_to == 'float':
                float(value)
            elif self.cast_to == 'unicode':
                str(value)
        except:
            raise colander.Invalid(node,
                                   "Can't cast {} to {}".format(
                                       value, self.cast_to))


def build_rule_schema(ruleset, check_matrix):
    """
    Accepts ruleset and a map of fields/possible operations and builds
    validation class
    """

    schema = colander.SchemaNode(colander.Mapping())
    schema.add(colander.SchemaNode(colander.String(), name='field'))

    if ruleset['field'] in ['__AND__', '__OR__', '__NOT__']:
        subrules = colander.SchemaNode(colander.Tuple(), name='rules')
        for rule in ruleset['rules']:
            subrules.add(build_rule_schema(rule, check_matrix))
        schema.add(subrules)
    else:
        op_choices = check_matrix[ruleset['field']]['ops']
        cast_to = check_matrix[ruleset['field']]['type']
        schema.add(colander.SchemaNode(colander.String(),
                                       validator=colander.OneOf(op_choices),
                                       name='op'))

        schema.add(colander.SchemaNode(colander.String(),
                                       name='value',
                                       validator=RuleFieldType(cast_to)))
    return schema


class ConfigTypeSchema(colander.MappingSchema):
    type = colander.SchemaNode(colander.String(), missing=None)
    config = colander.SchemaNode(UnknownType(), missing=None)


class MappingListSchema(colander.SequenceSchema):
    config = colander.SchemaNode(UnknownType())
