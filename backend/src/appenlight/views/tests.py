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
import logging
import datetime
import time
import random
import redis
import six
import pyramid.renderers
import requests

from ziggurat_foundations.models.services.user import UserService

import appenlight.celery.tasks
from pyramid.view import view_config
from pyramid_mailer.message import Message
from appenlight_client.timing import time_trace
from appenlight.models import DBSession, Datastores
from appenlight.models.user import User
from appenlight.models.report_group import ReportGroup
from appenlight.models.event import Event
from appenlight.models.services.report_group import ReportGroupService
from appenlight.models.services.event import EventService
from appenlight.lib.enums import ReportType

log = logging.getLogger(__name__)

GLOBAL_REQ = None


@view_config(route_name='test', match_param='action=mail',
             renderer='string', permission='root_administration')
def mail(request):
    """
    Test email communication
    """
    request.environ['HTTP_HOST'] = 'appenlight.com'
    request.environ['wsgi.url_scheme'] = 'https'
    renderer_vars = {"title": "You have just registered on AppEnlight",
                     "username": "test",
                     "email": "grzegżółka",
                     'firstname': 'dupa'}
    # return vars
    html = pyramid.renderers.render('/email_templates/registered.jinja2',
                                    renderer_vars,
                                    request=request)
    message = Message(subject="hello world %s" % random.randint(1, 9999),
                      sender="info@appenlight.com",
                      recipients=["ergo14@gmail.com"],
                      html=html)
    request.registry.mailer.send(message)
    return html
    return vars


@view_config(route_name='test', match_param='action=alerting',
             renderer='appenlight:templates/tests/alerting.jinja2',
             permission='root_administration')
def alerting_test(request):
    """
    Allows to test send data on various registered alerting channels
    """
    applications = UserService.resources_with_perms(request.user, ['view'], resource_types=['application'])
    # what we can select in total
    all_possible_app_ids = [app.resource_id for app in applications]
    resource = applications[0]

    alert_channels = []
    for channel in request.user.alert_channels:
        alert_channels.append(channel.get_dict())

    cname = request.params.get('channel_name')
    cvalue = request.params.get('channel_value')
    event_name = request.params.get('event_name')
    if cname and cvalue:
        for channel in request.user.alert_channels:
            if (channel.channel_value == cvalue and
                        channel.channel_name == cname):
                break
        if event_name in ['error_report_alert', 'slow_report_alert']:
            # opened
            new_event = Event(resource_id=resource.resource_id,
                              event_type=Event.types[event_name],
                              start_date=datetime.datetime.utcnow(),
                              status=Event.statuses['active'],
                              values={'reports': 5,
                                      'threshold': 10}
                              )
            channel.notify_alert(resource=resource,
                                 event=new_event,
                                 user=request.user,
                                 request=request)

            # closed
            ev_type = Event.types[event_name.replace('open', 'close')]
            new_event = Event(resource_id=resource.resource_id,
                              event_type=ev_type,
                              start_date=datetime.datetime.utcnow(),
                              status=Event.statuses['closed'],
                              values={'reports': 5,
                                      'threshold': 10})
            channel.notify_alert(resource=resource,
                                 event=new_event,
                                 user=request.user,
                                 request=request)
        elif event_name == 'notify_reports':
            report = ReportGroupService.by_app_ids(all_possible_app_ids) \
                .filter(ReportGroup.report_type == ReportType.error).first()
            confirmed_reports = [(5, report), (1, report)]
            channel.notify_reports(resource=resource,
                                   user=request.user,
                                   request=request,
                                   since_when=datetime.datetime.utcnow(),
                                   reports=confirmed_reports)
            confirmed_reports = [(5, report)]
            channel.notify_reports(resource=resource,
                                   user=request.user,
                                   request=request,
                                   since_when=datetime.datetime.utcnow(),
                                   reports=confirmed_reports)
        elif event_name == 'notify_uptime':
            new_event = Event(resource_id=resource.resource_id,
                              event_type=Event.types['uptime_alert'],
                              start_date=datetime.datetime.utcnow(),
                              status=Event.statuses['active'],
                              values={"status_code": 500,
                                      "tries": 2,
                                      "response_time": 0})
            channel.notify_uptime_alert(resource=resource,
                                        event=new_event,
                                        user=request.user,
                                        request=request)
        elif event_name == 'chart_alert':
            event = EventService.by_type_and_status(
                event_types=(Event.types['chart_alert'],),
                status_types=(Event.statuses['active'],)).first()
            channel.notify_chart_alert(resource=event.resource,
                                       event=event,
                                       user=request.user,
                                       request=request)
        elif event_name == 'daily_digest':
            since_when = datetime.datetime.utcnow() - datetime.timedelta(
                hours=8)
            filter_settings = {'resource': [resource.resource_id],
                               'tags': [{'name': 'type',
                                         'value': ['error'], 'op': None}],
                               'type': 'error', 'start_date': since_when}

            reports = ReportGroupService.get_trending(
                request, filter_settings=filter_settings, limit=50)
            channel.send_digest(resource=resource,
                                user=request.user,
                                request=request,
                                since_when=datetime.datetime.utcnow(),
                                reports=reports)

    return {'alert_channels': alert_channels,
            'applications': dict([(app.resource_id, app.resource_name)
                                  for app in applications.all()])}


@view_config(route_name='test', match_param='action=error',
             renderer='string', permission='root_administration')
def error(request):
    """
    Raises an internal error with some test data for testing purposes
    """
    request.environ['appenlight.message'] = 'test message'
    request.environ['appenlight.extra']['dupa'] = 'dupa'
    request.environ['appenlight.extra']['message'] = 'message'
    request.environ['appenlight.tags']['action'] = 'test_error'
    request.environ['appenlight.tags']['count'] = 5
    log.debug(chr(960))
    log.debug('debug')
    log.info(chr(960))
    log.info('INFO')
    log.warning('warning')

    @time_trace(name='error.foobar', min_duration=0.1)
    def fooobar():
        time.sleep(0.12)
        return 1

    fooobar()

    def foobar(somearg):
        raise Exception('test')

    client = redis.StrictRedis()
    client.setex('testval', 10, 'foo')
    request.environ['appenlight.force_send'] = 1

    # stats, result = get_local_storage(local_timing).get_thread_stats()
    # import pprint
    # pprint.pprint(stats)
    # pprint.pprint(result)
    # print 'entries', len(result)
    request.environ['appenlight.username'] = 'ErgO'
    raise Exception(chr(960) + '%s' % random.randint(1, 5))
    return {}


@view_config(route_name='test', match_param='action=task',
             renderer='string', permission='root_administration')
def test_task(request):
    """
    Test erroneous celery task
    """
    import appenlight.celery.tasks

    appenlight.celery.tasks.test_exception_task.delay()
    return 'task sent'


@view_config(route_name='test', match_param='action=task_retry',
             renderer='string', permission='root_administration')
def test_task_retry(request):
    """
    Test erroneous celery task
    """
    import appenlight.celery.tasks

    appenlight.celery.tasks.test_retry_exception_task.delay()
    return 'task sent'


@view_config(route_name='test', match_param='action=celery_emails',
             renderer='string', permission='root_administration')
def test_celery_emails(request):
    import appenlight.celery.tasks
    appenlight.celery.tasks.alerting.delay()
    return 'task sent'


@view_config(route_name='test', match_param='action=daily_digest',
             renderer='string', permission='root_administration')
def test_celery_daily_digest(request):
    import appenlight.celery.tasks
    appenlight.celery.tasks.daily_digest.delay()
    return 'task sent'


@view_config(route_name='test', match_param='action=celery_alerting',
             renderer='string', permission='root_administration')
def test_celery_alerting(request):
    import appenlight.celery.tasks
    appenlight.celery.tasks.alerting()
    return 'task sent'


@view_config(route_name='test', match_param='action=logging',
             renderer='string', permission='root_administration')
def logs(request):
    """
    Test some in-app logging
    """
    log.debug(chr(960))
    log.debug('debug')
    log.info(chr(960))
    log.info('INFO')
    log.warning('Matched GET /\xc4\x85\xc5\xbc\xc4\x87'
                '\xc4\x99\xc4\x99\xc4\x85/summary')
    log.warning('XXXXMatched GET /\xc4\x85\xc5\xbc\xc4'
                '\x87\xc4\x99\xc4\x99\xc4\x85/summary')
    log.warning('DUPA /ążćęęą')
    log.warning("g\u017ceg\u017c\u00f3\u0142ka")
    log.error('TEST Lorem ipsum2',
              extra={'user': 'ergo', 'commit': 'sog8ds0g7sdih12hh1j512h5k'})
    log.fatal('TEST Lorem ipsum3')
    log.warning('TEST Lorem ipsum',
                extra={"action": 'purchase',
                       "price": random.random() * 100,
                       "quantity": random.randint(1, 99)})
    log.warning('test_pkey',
                extra={"action": 'test_pkey', "price": random.random() * 100,
                       'ae_primary_key': 1,
                       "quantity": random.randint(1, 99)})
    log.warning('test_pkey2',
                extra={"action": 'test_pkey', "price": random.random() * 100,
                       'ae_primary_key': 'b',
                       'ae_permanent': 't',
                       "quantity": random.randint(1, 99)})
    log.warning('test_pkey3',
                extra={"action": 'test_pkey', "price": random.random() * 100,
                       'ae_primary_key': 1,
                       "quantity": random.randint(1, 99)})
    log.warning('test_pkey4',
                extra={"action": 'test_pkey', "price": random.random() * 100,
                       'ae_primary_key': 'b',
                       'ae_permanent': True,
                       "quantity": random.randint(1, 99)})
    request.environ['appenlight.force_send'] = 1
    return {}


@view_config(route_name='test', match_param='action=transaction',
             renderer='string', permission='root_administration')
def transaction_test(request):
    """
    Test transactions
    """
    try:
        result = DBSession.execute("SELECT 1/0")
    except:
        request.tm.abort()
    result = DBSession.execute("SELECT 1")
    return 'OK'


@view_config(route_name='test', match_param='action=slow_request',
             renderer='string', permission='root_administration')
def slow_request(request):
    """
    Test a request that has some slow entries - including nested calls
    """
    users = DBSession.query(User).all()
    import random
    some_val = random.random()
    import threading
    t_id = id(threading.currentThread())
    log.warning('slow_log %s %s ' % (some_val, t_id))
    log.critical('tid %s' % t_id)

    @time_trace(name='baz_func %s' % some_val, min_duration=0.1)
    def baz(arg):
        time.sleep(0.32)
        return arg

    requests.get('http://ubuntu.com')

    @time_trace(name='foo_func %s %s' % (some_val, t_id), min_duration=0.1)
    def foo(arg):
        time.sleep(0.52)
        log.warning('foo_func %s %s' % (some_val, t_id))
        requests.get('http://ubuntu.com?test=%s' % some_val)
        return bar(arg)

    @time_trace(name='bar_func %s %s' % (some_val, t_id), min_duration=0.1)
    def bar(arg):
        log.warning('bar_func %s %s' % (some_val, t_id))
        time.sleep(1.52)
        baz(arg)
        baz(arg)
        return baz(arg)

    foo('a')
    return {}


@view_config(route_name='test', match_param='action=styling',
             renderer='appenlight:templates/tests/styling.jinja2',
             permission='__no_permission_required__')
def styling(request):
    """
    Some styling test page
    """
    _ = str
    request.session.flash(_(
        'Your password got updated. '
        'Next time log in with your new credentials.'))
    request.session.flash(_(
        'Something went wrong when we '
        'tried to authorize you via external provider'),
        'warning')
    request.session.flash(_(
        'Unfortunately there was a problem '
        'processing your payment, please try again later.'),
        'error')
    return {}


@view_config(route_name='test', match_param='action=js_error',
             renderer='appenlight:templates/tests/js_error.jinja2',
             permission='__no_permission_required__')
def js(request):
    """
    Used for testing javasctipt client for error catching
    """
    return {}


@view_config(route_name='test', match_param='action=js_log',
             renderer='appenlight:templates/tests/js_log.jinja2',
             permission='__no_permission_required__')
def js_log(request):
    """
    Used for testing javasctipt client for logging
    """
    return {}


@view_config(route_name='test', match_param='action=log_requests',
             renderer='string',
             permission='__no_permission_required__')
def log_requests(request):
    """
    Util view for printing json requests
    """
    return {}


@view_config(route_name='test', match_param='action=url', renderer='string',
             permission='__no_permission_required__')
def log_requests(request):
    """
    I have no fucking clue why I needed that ;-)
    """
    return request.route_url('reports', _app_url='https://appenlight.com')


class TestClass(object):
    """
    Used to test if class-based view name resolution works correctly
    """

    def __init__(self, request):
        self.request = request

    @view_config(route_name='test', match_param='action=test_a',
                 renderer='string', permission='root_administration')
    @view_config(route_name='test', match_param='action=test_c',
                 renderer='string', permission='root_administration')
    @view_config(route_name='test', match_param='action=test_d',
                 renderer='string', permission='root_administration')
    def test_a(self):
        return 'ok'

    @view_config(route_name='test', match_param='action=test_b',
                 renderer='string', permission='root_administration')
    def test_b(self):
        return 'ok'
