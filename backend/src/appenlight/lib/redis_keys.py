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

BASE = 'appenlight:data:{}'

REDIS_KEYS = {
    'tasks': {
        'add_reports_lock': BASE.format('add_reports_lock:{}'),
        'add_logs_lock': BASE.format('add_logs_lock:{}'),
    },
    'counters': {
        'events_per_minute_per_user': BASE.format(
            'events_per_minute_per_user:{}:{}'),
        'reports_per_minute': BASE.format('reports_per_minute:{}'),
        'reports_per_hour_per_app': BASE.format(
            'reports_per_hour_per_app:{}:{}'),
        'reports_per_type': BASE.format('reports_per_type:{}'),
        'logs_per_minute': BASE.format('logs_per_minute:{}'),
        'logs_per_hour_per_app': BASE.format(
            'logs_per_hour_per_app:{}:{}'),
        'metrics_per_minute': BASE.format('metrics_per_minute:{}'),
        'metrics_per_hour_per_app': BASE.format(
            'metrics_per_hour_per_app:{}:{}'),
        'report_group_occurences': BASE.format('report_group_occurences:{}'),
        'report_group_occurences_alerting': BASE.format(
            'report_group_occurences_alerting:{}'),
        'report_group_occurences_10th': BASE.format(
            'report_group_occurences_10th:{}'),
        'report_group_occurences_100th': BASE.format(
            'report_group_occurences_100th:{}'),
    },
    'rate_limits': {
        'per_application_reports_rate_limit': BASE.format(
            'per_application_reports_limit:{}:{}'),
        'per_application_logs_rate_limit': BASE.format(
            'per_application_logs_rate_limit:{}:{}'),
        'per_application_metrics_rate_limit': BASE.format(
            'per_application_metrics_rate_limit:{}:{}'),
    },
    'apps_that_got_new_data_per_hour': BASE.format('apps_that_got_new_data_per_hour:{}'),
    'apps_that_had_reports': BASE.format('apps_that_had_reports'),
    'apps_that_had_error_reports': BASE.format('apps_that_had_error_reports'),
    'apps_that_had_reports_alerting': BASE.format(
        'apps_that_had_reports_alerting'),
    'apps_that_had_error_reports_alerting': BASE.format(
        'apps_that_had_error_reports_alerting'),
    'reports_to_notify_per_type_per_app': BASE.format(
        'reports_to_notify_per_type_per_app:{}:{}'),
    'reports_to_notify_per_type_per_app_alerting': BASE.format(
        'reports_to_notify_per_type_per_app_alerting:{}:{}'),
    'seen_tag_list': BASE.format('seen_tag_list')
}
