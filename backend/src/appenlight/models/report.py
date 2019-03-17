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

from datetime import datetime, timedelta
import math
import uuid
import hashlib
import copy
import urllib.parse
import logging
import sqlalchemy as sa

from appenlight.models import Base, Datastores
from appenlight.lib.utils.date_utils import convert_date
from appenlight.lib.utils import convert_es_type
from appenlight.models.slow_call import SlowCall
from appenlight.lib.utils import channelstream_request
from appenlight.lib.enums import ReportType, Language
from pyramid.threadlocal import get_current_registry, get_current_request
from sqlalchemy.dialects.postgresql import JSON
from ziggurat_foundations.models.base import BaseModel

log = logging.getLogger(__name__)

REPORT_TYPE_MATRIX = {
    'http_status': {"type": 'int',
                    "ops": ('eq', 'ne', 'ge', 'le',)},
    'group:priority': {"type": 'int',
                       "ops": ('eq', 'ne', 'ge', 'le',)},
    'duration': {"type": 'float',
                 "ops": ('ge', 'le',)},
    'url_domain': {"type": 'unicode',
                   "ops": ('eq', 'ne', 'startswith', 'endswith', 'contains',)},
    'url_path': {"type": 'unicode',
                 "ops": ('eq', 'ne', 'startswith', 'endswith', 'contains',)},
    'error': {"type": 'unicode',
              "ops": ('eq', 'ne', 'startswith', 'endswith', 'contains',)},
    'tags:server_name': {"type": 'unicode',
                         "ops": ('eq', 'ne', 'startswith', 'endswith',
                                 'contains',)},
    'traceback': {"type": 'unicode',
                  "ops": ('contains',)},
    'group:occurences': {"type": 'int',
                         "ops": ('eq', 'ne', 'ge', 'le',)}
}


class Report(Base, BaseModel):
    __tablename__ = 'reports'
    __table_args__ = {'implicit_returning': False}

    id = sa.Column(sa.Integer, nullable=False, primary_key=True)
    group_id = sa.Column(sa.BigInteger,
                         sa.ForeignKey('reports_groups.id', ondelete='cascade',
                                       onupdate='cascade'))
    resource_id = sa.Column(sa.Integer(), nullable=False, index=True)
    report_type = sa.Column(sa.Integer(), nullable=False, index=True)
    error = sa.Column(sa.UnicodeText(), index=True)
    extra = sa.Column(JSON(), default={})
    request = sa.Column(JSON(), nullable=False, default={})
    ip = sa.Column(sa.String(39), index=True, default='')
    username = sa.Column(sa.Unicode(255), default='')
    user_agent = sa.Column(sa.Unicode(255), default='')
    url = sa.Column(sa.UnicodeText(), index=True)
    request_id = sa.Column(sa.Text())
    request_stats = sa.Column(JSON(), nullable=False, default={})
    traceback = sa.Column(JSON(), nullable=False, default=None)
    traceback_hash = sa.Column(sa.Text())
    start_time = sa.Column(sa.DateTime(), default=datetime.utcnow,
                           server_default=sa.func.now())
    end_time = sa.Column(sa.DateTime())
    duration = sa.Column(sa.Float, default=0)
    http_status = sa.Column(sa.Integer, index=True)
    url_domain = sa.Column(sa.Unicode(100), index=True)
    url_path = sa.Column(sa.Unicode(255), index=True)
    tags = sa.Column(JSON(), nullable=False, default={})
    language = sa.Column(sa.Integer(), default=0)
    # this is used to determine partition for the report
    report_group_time = sa.Column(sa.DateTime(), default=datetime.utcnow,
                                  server_default=sa.func.now())

    logs = sa.orm.relationship(
        'Log',
        lazy='dynamic',
        passive_deletes=True,
        passive_updates=True,
        primaryjoin="and_(Report.request_id==Log.request_id, "
                    "Log.request_id != None, Log.request_id != '')",
        foreign_keys='[Log.request_id]')

    slow_calls = sa.orm.relationship('SlowCall',
                                     backref='detail',
                                     cascade="all, delete-orphan",
                                     passive_deletes=True,
                                     passive_updates=True,
                                     order_by='SlowCall.timestamp')

    def set_data(self, data, resource, protocol_version=None):
        self.http_status = data['http_status']
        self.priority = data['priority']
        self.error = data['error']
        report_language = data.get('language', '').lower()
        self.language = getattr(Language, report_language, Language.unknown)
        # we need temp holder here to decide later
        # if we want to to commit the tags if report is marked for creation
        self.tags = {
            'server_name': data['server'],
            'view_name': data['view_name']
        }
        if data.get('tags'):
            for tag_tuple in data['tags']:
                self.tags[tag_tuple[0]] = tag_tuple[1]
        self.traceback = data['traceback']
        stripped_traceback = self.stripped_traceback()
        tb_repr = repr(stripped_traceback).encode('utf8')
        self.traceback_hash = hashlib.sha1(tb_repr).hexdigest()
        url_info = urllib.parse.urlsplit(
            data.get('url', ''), allow_fragments=False)
        self.url_domain = url_info.netloc[:128]
        self.url_path = url_info.path[:2048]
        self.occurences = data['occurences']
        if self.error:
            self.report_type = ReportType.error
        else:
            self.report_type = ReportType.slow

        # but if its status 404 its 404 type
        if self.http_status in [404, '404'] or self.error == '404 Not Found':
            self.report_type = ReportType.not_found
            self.error = ''

        self.generate_grouping_hash(data.get('appenlight.group_string',
                                             data.get('group_string')),
                                    resource.default_grouping,
                                    protocol_version)

        # details
        if data['http_status'] in [404, '404']:
            data = {"username": data["username"],
                    "ip": data["ip"],
                    "url": data["url"],
                    "user_agent": data["user_agent"]}
            if data.get('HTTP_REFERER') or data.get('http_referer'):
                data['HTTP_REFERER'] = data.get(
                    'HTTP_REFERER', '') or data.get('http_referer', '')

        self.resource_id = resource.resource_id
        self.username = data['username']
        self.user_agent = data['user_agent']
        self.ip = data['ip']
        self.extra = {}
        if data.get('extra'):
            for extra_tuple in data['extra']:
                self.extra[extra_tuple[0]] = extra_tuple[1]

        self.url = data['url']
        self.request_id = data.get('request_id', '').replace('-', '') or str(
            uuid.uuid4())
        request_data = data.get('request', {})

        self.request = request_data
        self.request_stats = data.get('request_stats', {})
        traceback = data.get('traceback')
        if not traceback:
            traceback = data.get('frameinfo')
        self.traceback = traceback
        start_date = convert_date(data.get('start_time'))
        if not self.start_time or self.start_time < start_date:
            self.start_time = start_date

        self.end_time = convert_date(data.get('end_time'), False)
        self.duration = 0

        if self.start_time and self.end_time:
            d = self.end_time - self.start_time
            self.duration = d.total_seconds()

        # update tags with other vars
        if self.username:
            self.tags['user_name'] = self.username
        self.tags['report_language'] = Language.key_from_value(self.language)

    def add_slow_calls(self, data, report_group):
        slow_calls = []
        for call in data.get('slow_calls', []):
            sc_inst = SlowCall()
            sc_inst.set_data(call, resource_id=self.resource_id,
                             report_group=report_group)
            slow_calls.append(sc_inst)
            self.slow_calls.extend(slow_calls)
        return slow_calls

    def get_dict(self, request, details=False, exclude_keys=None,
                 include_keys=None):
        from appenlight.models.services.report_group import ReportGroupService
        instance_dict = super(Report, self).get_dict()
        instance_dict['req_stats'] = self.req_stats()
        instance_dict['group'] = {}
        instance_dict['group']['id'] = self.report_group.id
        instance_dict['group'][
            'total_reports'] = self.report_group.total_reports
        instance_dict['group']['last_report'] = self.report_group.last_report
        instance_dict['group']['priority'] = self.report_group.priority
        instance_dict['group']['occurences'] = self.report_group.occurences
        instance_dict['group'][
            'last_timestamp'] = self.report_group.last_timestamp
        instance_dict['group'][
            'first_timestamp'] = self.report_group.first_timestamp
        instance_dict['group']['public'] = self.report_group.public
        instance_dict['group']['fixed'] = self.report_group.fixed
        instance_dict['group']['read'] = self.report_group.read
        instance_dict['group'][
            'average_duration'] = self.report_group.average_duration

        instance_dict[
            'resource_name'] = self.report_group.application.resource_name
        instance_dict['report_type'] = self.report_type

        if instance_dict['http_status'] == 404 and not instance_dict['error']:
            instance_dict['error'] = '404 Not Found'

        if details:
            instance_dict['affected_users_count'] = \
                ReportGroupService.affected_users_count(self.report_group)
            instance_dict['top_affected_users'] = [
                {'username': u.username, 'count': u.count} for u in
                ReportGroupService.top_affected_users(self.report_group)]
            instance_dict['application'] = {'integrations': []}
            for integration in self.report_group.application.integrations:
                if integration.front_visible:
                    instance_dict['application']['integrations'].append(
                        {'name': integration.integration_name,
                         'action': integration.integration_action})
            instance_dict['comments'] = [c.get_dict() for c in
                                         self.report_group.comments]

            instance_dict['group']['next_report'] = None
            instance_dict['group']['previous_report'] = None
            next_in_group = self.get_next_in_group(request)
            previous_in_group = self.get_previous_in_group(request)
            if next_in_group:
                instance_dict['group']['next_report'] = next_in_group
            if previous_in_group:
                instance_dict['group']['previous_report'] = previous_in_group

            # slow call ordering
            def find_parent(row, data):
                for r in reversed(data):
                    try:
                        if (row['timestamp'] > r['timestamp'] and
                                    row['end_time'] < r['end_time']):
                            return r
                    except TypeError as e:
                        log.warning('reports_view.find_parent: %s' % e)
                return None

            new_calls = []
            calls = [c.get_dict() for c in self.slow_calls]
            while calls:
                # start from end
                for x in range(len(calls) - 1, -1, -1):
                    parent = find_parent(calls[x], calls)
                    if parent:
                        parent['children'].append(calls[x])
                    else:
                        # no parent at all? append to new calls anyways
                        new_calls.append(calls[x])
                        # print 'append', calls[x]
                    del calls[x]
                    break
            instance_dict['slow_calls'] = new_calls

        instance_dict['front_url'] = self.get_public_url(request)

        exclude_keys_list = exclude_keys or []
        include_keys_list = include_keys or []
        for k in list(instance_dict.keys()):
            if k == 'group':
                continue
            if (k in exclude_keys_list or
                    (k not in include_keys_list and include_keys)):
                del instance_dict[k]
        return instance_dict

    def get_previous_in_group(self, request):
        query = {
            "size": 1,
            "query": {
                "filtered": {
                    "filter": {
                        "and": [{"term": {"group_id": self.group_id}},
                                {"range": {"pg_id": {"lt": self.id}}}]
                    }
                }
            },
            "sort": [
                {"_doc": {"order": "desc"}},
            ],
        }
        result = request.es_conn.search(body=query, index=self.partition_id,
                                        doc_type='report')
        if result['hits']['total']:
            return result['hits']['hits'][0]['_source']['pg_id']

    def get_next_in_group(self, request):
        query = {
            "size": 1,
            "query": {
                "filtered": {
                    "filter": {
                        "and": [{"term": {"group_id": self.group_id}},
                                {"range": {"pg_id": {"gt": self.id}}}]
                    }
                }
            },
            "sort": [
                {"_doc": {"order": "asc"}},
            ],
        }
        result = request.es_conn.search(body=query, index=self.partition_id,
                                        doc_type='report')
        if result['hits']['total']:
            return result['hits']['hits'][0]['_source']['pg_id']

    def get_public_url(self, request=None, report_group=None, _app_url=None):
        """
        Returns url that user can use to visit specific report
        """
        if not request:
            request = get_current_request()
        url = request.route_url('/', _app_url=_app_url)
        if report_group:
            return (url + 'ui/report/%s/%s') % (report_group.id, self.id)
        return (url + 'ui/report/%s/%s') % (self.group_id, self.id)

    def req_stats(self):
        stats = self.request_stats.copy()
        stats['percentages'] = {}
        stats['percentages']['main'] = 100.0
        main = stats.get('main', 0.0)
        if not main:
            return None
        for name, call_time in stats.items():
            if ('calls' not in name and 'main' not in name and
                        'percentages' not in name):
                stats['main'] -= call_time
                stats['percentages'][name] = math.floor(
                    (call_time / main * 100.0))
                stats['percentages']['main'] -= stats['percentages'][name]
        if stats['percentages']['main'] < 0.0:
            stats['percentages']['main'] = 0.0
            stats['main'] = 0.0
        return stats

    def generate_grouping_hash(self, hash_string=None, default_grouping=None,
                               protocol_version=None):
        """
        Generates SHA1 hash that will be used to group reports together
        """
        if not hash_string:
            location = self.tags.get('view_name') or self.url_path;
            server_name = self.tags.get('server_name') or ''
            if default_grouping == 'url_traceback':
                hash_string = '%s_%s_%s' % (self.traceback_hash, location,
                                            self.error)
                if self.language == Language.javascript:
                    hash_string = '%s_%s' % (self.traceback_hash, self.error)

            elif default_grouping == 'traceback_server':
                hash_string = '%s_%s' % (self.traceback_hash, server_name)
                if self.language == Language.javascript:
                    hash_string = '%s_%s' % (self.traceback_hash, server_name)
            else:
                hash_string = '%s_%s' % (self.error, location)
        month = datetime.utcnow().date().replace(day=1)
        hash_string = '{}_{}'.format(month, hash_string)
        binary_string = hash_string.encode('utf8')
        self.grouping_hash = hashlib.sha1(binary_string).hexdigest()
        return self.grouping_hash

    def stripped_traceback(self):
        """
        Traceback without local vars
        """
        stripped_traceback = copy.deepcopy(self.traceback)

        if isinstance(stripped_traceback, list):
            for row in stripped_traceback:
                row.pop('vars', None)
        return stripped_traceback

    def notify_channel(self, report_group):
        """
        Sends notification to websocket channel
        """
        settings = get_current_registry().settings
        log.info('notify channelstream')
        if self.report_type != ReportType.error:
            return
        payload = {
            'type': 'message',
            "user": '__system__',
            "channel": 'app_%s' % self.resource_id,
            'message': {
                'topic': 'front_dashboard.new_topic',
                'report': {
                    'group': {
                        'priority': report_group.priority,
                        'first_timestamp': report_group.first_timestamp,
                        'last_timestamp': report_group.last_timestamp,
                        'average_duration': report_group.average_duration,
                        'occurences': report_group.occurences
                    },
                    'report_id': self.id,
                    'group_id': self.group_id,
                    'resource_id': self.resource_id,
                    'http_status': self.http_status,
                    'url_domain': self.url_domain,
                    'url_path': self.url_path,
                    'error': self.error or '',
                    'server': self.tags.get('server_name'),
                    'view_name': self.tags.get('view_name'),
                    'front_url': self.get_public_url(),
                }
            }

        }
        channelstream_request(settings['cometd.secret'], '/message', [payload],
                              servers=[settings['cometd_servers']])

    def es_doc(self):
        tags = {}
        tag_list = []
        for name, value in self.tags.items():
            name = name.replace('.', '_')
            tag_list.append(name)
            tags[name] = {
                "values": convert_es_type(value),
                "numeric_values": value if (
                    isinstance(value, (int, float)) and
                    not isinstance(value, bool)) else None}

        if 'user_name' not in self.tags and self.username:
            tags["user_name"] = {"value": [self.username],
                                 "numeric_value": None}
        return {
            '_id': str(self.id),
            'pg_id': str(self.id),
            'resource_id': self.resource_id,
            'http_status': self.http_status or '',
            'start_time': self.start_time,
            'end_time': self.end_time,
            'url_domain': self.url_domain if self.url_domain else '',
            'url_path': self.url_path if self.url_path else '',
            'duration': self.duration,
            'error': self.error if self.error else '',
            'report_type': self.report_type,
            'request_id': self.request_id,
            'ip': self.ip,
            'group_id': str(self.group_id),
            '_parent': str(self.group_id),
            'tags': tags,
            'tag_list': tag_list
        }

    @property
    def partition_id(self):
        return 'rcae_r_%s' % self.report_group_time.strftime('%Y_%m')

    def partition_range(self):
        start_date = self.report_group_time.date().replace(day=1)
        end_date = start_date + timedelta(days=40)
        end_date = end_date.replace(day=1)
        return start_date, end_date


def after_insert(mapper, connection, target):
    if not hasattr(target, '_skip_ft_index'):
        data = target.es_doc()
        data.pop('_id', None)
        Datastores.es.index(target.partition_id, 'report', data,
                            parent=target.group_id, id=target.id)


def after_update(mapper, connection, target):
    if not hasattr(target, '_skip_ft_index'):
        data = target.es_doc()
        data.pop('_id', None)
        Datastores.es.index(target.partition_id, 'report', data,
                            parent=target.group_id, id=target.id)


def after_delete(mapper, connection, target):
    if not hasattr(target, '_skip_ft_index'):
        query = {"query":{'term': {'pg_id': target.id}}}
        Datastores.es.transport.perform_request("DELETE", '/{}/{}/_query'.format(target.partition_id, 'report'), body=query)


sa.event.listen(Report, 'after_insert', after_insert)
sa.event.listen(Report, 'after_update', after_update)
sa.event.listen(Report, 'after_delete', after_delete)
