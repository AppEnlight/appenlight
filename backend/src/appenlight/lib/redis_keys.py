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
