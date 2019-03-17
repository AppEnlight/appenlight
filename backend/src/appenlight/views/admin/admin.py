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

import logging
import os
import pkg_resources

from datetime import datetime, timedelta

import psutil
import redis

from pyramid.view import view_config
from appenlight.models import DBSession
from appenlight.models import Datastores
from appenlight.lib.redis_keys import REDIS_KEYS


def bytes2human(total):
    giga = 1024.0 ** 3
    mega = 1024.0 ** 2
    kilo = 1024.0
    if giga <= total:
        return '{:0.1f}G'.format(total / giga)
    elif mega <= total:
        return '{:0.1f}M'.format(total / mega)
    else:
        return '{:0.1f}K'.format(total / kilo)


log = logging.getLogger(__name__)


@view_config(route_name='section_view',
             match_param=['section=admin_section', 'view=system'],
             renderer='json', permission='root_administration')
def system(request):
    current_time = datetime.utcnow(). \
                       replace(second=0, microsecond=0) - timedelta(minutes=1)
    # global app counter
    processed_reports = request.registry.redis_conn.get(
        REDIS_KEYS['counters']['reports_per_minute'].format(current_time))
    processed_reports = int(processed_reports) if processed_reports else 0
    processed_logs = request.registry.redis_conn.get(
        REDIS_KEYS['counters']['logs_per_minute'].format(current_time))
    processed_logs = int(processed_logs) if processed_logs else 0
    processed_metrics = request.registry.redis_conn.get(
        REDIS_KEYS['counters']['metrics_per_minute'].format(current_time))
    processed_metrics = int(processed_metrics) if processed_metrics else 0

    waiting_reports = 0
    waiting_logs = 0
    waiting_metrics = 0
    waiting_other = 0

    if 'redis' in request.registry.settings['celery.broker_type']:
        redis_client = redis.StrictRedis.from_url(
            request.registry.settings['celery.broker_url'])
        waiting_reports = redis_client.llen('reports')
        waiting_logs = redis_client.llen('logs')
        waiting_metrics = redis_client.llen('metrics')
        waiting_other = redis_client.llen('default')

    # process
    def replace_inf(val):
        return val if val != psutil.RLIM_INFINITY else 'unlimited'

    p = psutil.Process()
    fd = p.rlimit(psutil.RLIMIT_NOFILE)
    memlock = p.rlimit(psutil.RLIMIT_MEMLOCK)
    self_info = {
        'fds': {'soft': replace_inf(fd[0]),
                'hard': replace_inf(fd[1])},
        'memlock': {'soft': replace_inf(memlock[0]),
                    'hard': replace_inf(memlock[1])},
    }

    # disks
    disks = []
    for part in psutil.disk_partitions(all=False):
        if os.name == 'nt':
            if 'cdrom' in part.opts or part.fstype == '':
                continue
        usage = psutil.disk_usage(part.mountpoint)
        disks.append({
            'device': part.device,
            'total': bytes2human(usage.total),
            'used': bytes2human(usage.used),
            'free': bytes2human(usage.free),
            'percentage': int(usage.percent),
            'mountpoint': part.mountpoint,
            'fstype': part.fstype
        })

    # memory
    memory_v = psutil.virtual_memory()
    memory_s = psutil.swap_memory()

    memory = {
        'total': bytes2human(memory_v.total),
        'available': bytes2human(memory_v.available),
        'percentage': memory_v.percent,
        'used': bytes2human(memory_v.used),
        'free': bytes2human(memory_v.free),
        'active': bytes2human(memory_v.active),
        'inactive': bytes2human(memory_v.inactive),
        'buffers': bytes2human(memory_v.buffers),
        'cached': bytes2human(memory_v.cached),
        'swap_total': bytes2human(memory_s.total),
        'swap_used': bytes2human(memory_s.used)
    }

    # load
    system_load = os.getloadavg()

    # processes
    min_mem = 1024 * 1024 * 40  # 40MB
    process_info = []
    for p in psutil.process_iter():
        mem_used = p.memory_info().rss
        if mem_used < min_mem:
            continue
        process_info.append({'owner': p.username(),
                             'pid': p.pid,
                             'cpu': round(p.cpu_percent(interval=0), 1),
                             'mem_percentage': round(p.memory_percent(),1),
                             'mem_usage': bytes2human(mem_used),
                             'name': p.name(),
                             'command': ' '.join(p.cmdline())
                             })
    process_info = sorted(process_info, key=lambda x: x['mem_percentage'],
                          reverse=True)

    # pg tables

    db_size_query = '''
    SELECT tablename, pg_total_relation_size(tablename::text) size
    FROM pg_tables WHERE tablename NOT LIKE 'pg_%' AND 
    tablename NOT LIKE 'sql_%' ORDER BY size DESC;'''

    db_tables = []
    for row in DBSession.execute(db_size_query):
        db_tables.append({"size_human": bytes2human(row.size),
                          "table_name": row.tablename})

    # es indices
    es_indices = []
    result = Datastores.es.indices.stats(metric=['store, docs'])
    for ix, stats in result['indices'].items():
        size = stats['primaries']['store']['size_in_bytes']
        es_indices.append({'name': ix,
                           'size': size,
                           'size_human': bytes2human(size)})

    # packages

    packages = ({'name': p.project_name, 'version': p.version}
                for p in pkg_resources.working_set)

    return {'db_tables': db_tables,
            'es_indices': sorted(es_indices,
                                 key=lambda x: x['size'], reverse=True),
            'process_info': process_info,
            'system_load': system_load,
            'disks': disks,
            'memory': memory,
            'packages': sorted(packages, key=lambda x: x['name'].lower()),
            'current_time': current_time,
            'queue_stats': {
                'processed_reports': processed_reports,
                'processed_logs': processed_logs,
                'processed_metrics': processed_metrics,
                'waiting_reports': waiting_reports,
                'waiting_logs': waiting_logs,
                'waiting_metrics': waiting_metrics,
                'waiting_other': waiting_other
            },
            'self_info': self_info
            }
