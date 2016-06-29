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

import wtforms
import formencode
import re
import pyramid.threadlocal
import datetime
import appenlight.lib.helpers as h

from appenlight.models.user import User
from appenlight.models.group import Group
from appenlight.models import DBSession
from appenlight.models.alert_channel import AlertChannel
from appenlight.models.integrations import IntegrationException
from appenlight.models.integrations.campfire import CampfireIntegration
from appenlight.models.integrations.bitbucket import BitbucketIntegration
from appenlight.models.integrations.github import GithubIntegration
from appenlight.models.integrations.flowdock import FlowdockIntegration
from appenlight.models.integrations.hipchat import HipchatIntegration
from appenlight.models.integrations.jira import JiraClient
from appenlight.models.integrations.slack import SlackIntegration
from appenlight.lib.ext_json import json
from wtforms.ext.csrf.form import SecureForm
from wtforms.compat import iteritems
from collections import defaultdict

_ = str

strip_filter = lambda x: x.strip() if x else None
uppercase_filter = lambda x: x.upper() if x else None

FALSE_VALUES = ('false', '', False, None)


class CSRFException(Exception):
    pass


class ReactorForm(SecureForm):
    def __init__(self, formdata=None, obj=None, prefix='', csrf_context=None,
                 **kwargs):
        super(ReactorForm, self).__init__(formdata=formdata, obj=obj,
                                          prefix=prefix,
                                          csrf_context=csrf_context, **kwargs)
        self._csrf_context = csrf_context

    def generate_csrf_token(self, csrf_context):
        return csrf_context.session.get_csrf_token()

    def validate_csrf_token(self, field):
        request = self._csrf_context or pyramid.threadlocal.get_current_request()
        is_from_auth_token = 'auth:auth_token' in request.effective_principals
        if is_from_auth_token:
            return True

        if field.data != field.current_token:
            # try to save the day by using token from angular
            if request.headers.get('X-XSRF-TOKEN') != field.current_token:
                raise CSRFException('Invalid CSRF token')

    @property
    def errors_dict(self):
        r_dict = defaultdict(list)
        for k, errors in self.errors.items():
            r_dict[k].extend([str(e) for e in errors])
        return r_dict

    @property
    def errors_json(self):
        return json.dumps(self.errors_dict)

    def populate_obj(self, obj, ignore_none=False):
        """
        Populates the attributes of the passed `obj` with data from the form's
        fields.

        :note: This is a destructive operation; Any attribute with the same name
               as a field will be overridden. Use with caution.
        """
        if ignore_none:
            for name, field in iteritems(self._fields):
                if field.data is not None:
                    field.populate_obj(obj, name)
        else:
            for name, field in iteritems(self._fields):
                field.populate_obj(obj, name)

    css_classes = {}
    ignore_labels = {}


class SignInForm(ReactorForm):
    came_from = wtforms.HiddenField()
    sign_in_user_name = wtforms.StringField(_('User Name'))
    sign_in_user_password = wtforms.PasswordField(_('Password'))

    ignore_labels = ['submit']
    css_classes = {'submit': 'btn btn-primary'}

    html_attrs = {'sign_in_user_name': {'placeholder': 'Your login'},
                  'sign_in_user_password': {
                      'placeholder': 'Your password'}}


from wtforms.widgets import html_params, HTMLString


def select_multi_checkbox(field, ul_class='set', **kwargs):
    """Render a multi-checkbox widget"""
    kwargs.setdefault('type', 'checkbox')
    field_id = kwargs.pop('id', field.id)
    html = ['<ul %s>' % html_params(id=field_id, class_=ul_class)]
    for value, label, checked in field.iter_choices():
        choice_id = '%s-%s' % (field_id, value)
        options = dict(kwargs, name=field.name, value=value, id=choice_id)
        if checked:
            options['checked'] = 'checked'
        html.append('<li><input %s /> ' % html_params(**options))
        html.append('<label for="%s">%s</label></li>' % (choice_id, label))
    html.append('</ul>')
    return HTMLString(''.join(html))


def button_widget(field, button_cls='ButtonField btn btn-default', **kwargs):
    """Render a button widget"""
    kwargs.setdefault('type', 'button')
    field_id = kwargs.pop('id', field.id)
    kwargs.setdefault('value', field.label.text)
    html = ['<button %s>%s</button>' % (html_params(id=field_id,
                                                     class_=button_cls),
                                         kwargs['value'],)]
    return HTMLString(''.join(html))


def clean_whitespace(value):
    if value:
        return value.strip()
    return value


def found_username_validator(form, field):
    user = User.by_user_name(field.data)
    # sets user to recover in email validator
    form.field_user = user
    if not user:
        raise wtforms.ValidationError('This username does not exist')


def found_username_email_validator(form, field):
    user = User.by_email(field.data)
    if not user:
        raise wtforms.ValidationError('Email is incorrect')


def unique_username_validator(form, field):
    user = User.by_user_name(field.data)
    if user:
        raise wtforms.ValidationError('This username already exists in system')


def unique_groupname_validator(form, field):
    group = Group.by_group_name(field.data)
    mod_group = getattr(form, '_modified_group', None)
    if group and (not mod_group or mod_group.id != group.id):
        raise wtforms.ValidationError(
            'This group name already exists in system')


def unique_email_validator(form, field):
    user = User.by_email(field.data)
    if user:
        raise wtforms.ValidationError('This email already exists in system')


def email_validator(form, field):
    validator = formencode.validators.Email()
    try:
        validator.to_python(field.data)
    except formencode.Invalid as e:
        raise wtforms.ValidationError(e)


def unique_alert_email_validator(form, field):
    q = DBSession.query(AlertChannel)
    q = q.filter(AlertChannel.channel_name == 'email')
    q = q.filter(AlertChannel.channel_value == field.data)
    email = q.first()
    if email:
        raise wtforms.ValidationError(
            'This email already exists in alert system')


def blocked_email_validator(form, field):
    blocked_emails = [
        'goood-mail.org',
        'shoeonlineblog.com',
        'louboutinemart.com',
        'guccibagshere.com',
        'nikeshoesoutletforsale.com'
    ]
    data = field.data or ''
    domain = data.split('@')[-1]
    if domain in blocked_emails:
        raise wtforms.ValidationError('Don\'t spam')


def old_password_validator(form, field):
    if not field.user.check_password(field.data or ''):
        raise wtforms.ValidationError('You need to enter correct password')


class UserRegisterForm(ReactorForm):
    user_name = wtforms.StringField(
        _('User Name'),
        filters=[strip_filter],
        validators=[
            wtforms.validators.Length(min=2, max=30),
            wtforms.validators.Regexp(
                re.compile(r'^[\.\w-]+$', re.UNICODE),
                message="Invalid characters used"),
            unique_username_validator,
            wtforms.validators.DataRequired()
        ])

    user_password = wtforms.PasswordField(_('User Password'),
                                          filters=[strip_filter],
                                          validators=[
                                              wtforms.validators.Length(min=4),
                                              wtforms.validators.DataRequired()
                                          ])

    email = wtforms.StringField(_('Email Address'),
                                filters=[strip_filter],
                                validators=[email_validator,
                                            unique_email_validator,
                                            blocked_email_validator,
                                            wtforms.validators.DataRequired()],
                                description=_("We promise we will not share "
                                              "your email with anyone"))
    first_name = wtforms.HiddenField(_('First Name'))
    last_name = wtforms.HiddenField(_('Last Name'))

    ignore_labels = ['submit']
    css_classes = {'submit': 'btn btn-primary'}

    html_attrs = {'user_name': {'placeholder': 'Your login'},
                  'user_password': {'placeholder': 'Your password'},
                  'email': {'placeholder': 'Your email'}}


class UserCreateForm(UserRegisterForm):
    status = wtforms.BooleanField('User status',
                                  false_values=FALSE_VALUES)


class UserUpdateForm(UserCreateForm):
    user_name = None
    user_password = wtforms.PasswordField(_('User Password'),
                                          filters=[strip_filter],
                                          validators=[
                                              wtforms.validators.Length(min=4),
                                              wtforms.validators.Optional()
                                          ])
    email = wtforms.StringField(_('Email Address'),
                                filters=[strip_filter],
                                validators=[email_validator,
                                            wtforms.validators.DataRequired()])


class LostPasswordForm(ReactorForm):
    email = wtforms.StringField(_('Email Address'),
                                filters=[strip_filter],
                                validators=[email_validator,
                                            found_username_email_validator,
                                            wtforms.validators.DataRequired()])

    submit = wtforms.SubmitField(_('Reset password'))
    ignore_labels = ['submit']
    css_classes = {'submit': 'btn btn-primary'}


class ChangePasswordForm(ReactorForm):
    old_password = wtforms.PasswordField(
        'Old Password',
        filters=[strip_filter],
        validators=[old_password_validator,
                    wtforms.validators.DataRequired()])

    new_password = wtforms.PasswordField(
        'New Password',
        filters=[strip_filter],
        validators=[wtforms.validators.Length(min=4),
                    wtforms.validators.DataRequired()])
    new_password_confirm = wtforms.PasswordField(
        'Confirm Password',
        filters=[strip_filter],
        validators=[wtforms.validators.EqualTo('new_password'),
                    wtforms.validators.DataRequired()])
    submit = wtforms.SubmitField('Change Password')
    ignore_labels = ['submit']
    css_classes = {'submit': 'btn btn-primary'}


class CheckPasswordForm(ReactorForm):
    password = wtforms.PasswordField(
        'Password',
        filters=[strip_filter],
        validators=[old_password_validator,
                    wtforms.validators.DataRequired()])


class NewPasswordForm(ReactorForm):
    new_password = wtforms.PasswordField(
        'New Password',
        filters=[strip_filter],
        validators=[wtforms.validators.Length(min=4),
                    wtforms.validators.DataRequired()])
    new_password_confirm = wtforms.PasswordField(
        'Confirm Password',
        filters=[strip_filter],
        validators=[wtforms.validators.EqualTo('new_password'),
                    wtforms.validators.DataRequired()])
    submit = wtforms.SubmitField('Set Password')
    ignore_labels = ['submit']
    css_classes = {'submit': 'btn btn-primary'}


class CORSTextAreaField(wtforms.StringField):
    """
    This field represents an HTML ``<textarea>`` and can be used to take
    multi-line input.
    """
    widget = wtforms.widgets.TextArea()

    def process_formdata(self, valuelist):
        self.data = []
        if valuelist:
            data = [x.strip() for x in valuelist[0].split('\n')]
            for d in data:
                if not d:
                    continue
                if d.startswith('www.'):
                    d = d[4:]
                if data:
                    self.data.append(d)
        else:
            self.data = []
        self.data = '\n'.join(self.data)


class ApplicationCreateForm(ReactorForm):
    resource_name = wtforms.StringField(
        _('Application name'),
        filters=[strip_filter],
        validators=[wtforms.validators.Length(min=1),
                    wtforms.validators.DataRequired()])

    domains = CORSTextAreaField(
        _('Domain names for CORS headers '),
        validators=[wtforms.validators.Length(min=1),
                    wtforms.validators.Optional()],
        description='Required for Javascript error '
                    'tracking (one line one domain, skip http:// part)')

    submit = wtforms.SubmitField(_('Create Application'))

    ignore_labels = ['submit']
    css_classes = {'submit': 'btn btn-primary'}
    html_attrs = {'resource_name': {'placeholder': 'Application Name'},
                  'uptime_url': {'placeholder': 'http://somedomain.com'}}


class ApplicationUpdateForm(ApplicationCreateForm):
    default_grouping = wtforms.SelectField(
        _('Default grouping for errors'),
        choices=[('url_type', 'Error Type + location',),
                 ('url_traceback', 'Traceback + location',),
                 ('traceback_server', 'Traceback + Server',)],
        default='url_traceback')

    error_report_threshold = wtforms.IntegerField(
        _('Alert on error reports'),
        validators=[
            wtforms.validators.NumberRange(min=1),
            wtforms.validators.DataRequired()
        ],
        description='Application requires to send at least this amount of '
                    'error reports per minute to open alert'
    )

    slow_report_threshold = wtforms.IntegerField(
        _('Alert on slow reports'),
        validators=[wtforms.validators.NumberRange(min=1),
                    wtforms.validators.DataRequired()],
        description='Application requires to send at least this amount of '
                    'slow reports per minute to open alert')

    allow_permanent_storage = wtforms.BooleanField(
        _('Permanent logs'),
        false_values=FALSE_VALUES,
        description=_(
            'Allow permanent storage of logs in separate DB partitions'))

    submit = wtforms.SubmitField(_('Create Application'))


class UserSearchSchemaForm(ReactorForm):
    user_name = wtforms.StringField('User Name',
                                    filters=[strip_filter], )

    submit = wtforms.SubmitField(_('Search User'))
    ignore_labels = ['submit']
    css_classes = {'submit': 'btn btn-primary'}

    '<li class="user_exists"><span></span></li>'


class YesNoForm(ReactorForm):
    no = wtforms.SubmitField('No', default='')
    yes = wtforms.SubmitField('Yes', default='')
    ignore_labels = ['submit']
    css_classes = {'submit': 'btn btn-primary'}


status_codes = [('', 'All',), ('500', '500',), ('404', '404',)]

priorities = [('', 'All',)]
for i in range(1, 11):
    priorities.append((str(i), str(i),))

report_status_choices = [('', 'All',),
                         ('never_reviewed', 'Never revieved',),
                         ('reviewed', 'Revieved',),
                         ('public', 'Public',),
                         ('fixed', 'Fixed',), ]


class ReportBrowserForm(ReactorForm):
    applications = wtforms.SelectMultipleField('Applications',
                                               widget=select_multi_checkbox)
    http_status = wtforms.SelectField('HTTP Status', choices=status_codes)
    priority = wtforms.SelectField('Priority', choices=priorities, default='')
    start_date = wtforms.DateField('Start Date')
    end_date = wtforms.DateField('End Date')
    error = wtforms.StringField('Error')
    url_path = wtforms.StringField('URL Path')
    url_domain = wtforms.StringField('URL Domain')
    report_status = wtforms.SelectField('Report status',
                                        choices=report_status_choices,
                                        default='')
    submit = wtforms.SubmitField('<span class="glyphicon glyphicon-search">'
                                 '</span> Filter results',
                                 widget=button_widget)

    ignore_labels = ['submit']
    css_classes = {'submit': 'btn btn-primary'}


slow_report_status_choices = [('', 'All',),
                              ('never_reviewed', 'Never revieved',),
                              ('reviewed', 'Revieved',),
                              ('public', 'Public',), ]


class BulkOperationForm(ReactorForm):
    applications = wtforms.SelectField('Applications')
    start_date = wtforms.DateField(
        'Start Date',
        default=lambda: datetime.datetime.utcnow() - datetime.timedelta(
            days=90))
    end_date = wtforms.DateField('End Date')
    confirm = wtforms.BooleanField(
        'Confirm operation',
        validators=[wtforms.validators.DataRequired()])


class LogBrowserForm(ReactorForm):
    applications = wtforms.SelectMultipleField('Applications',
                                               widget=select_multi_checkbox)
    start_date = wtforms.DateField('Start Date')
    log_level = wtforms.StringField('Log level')
    message = wtforms.StringField('Message')
    namespace = wtforms.StringField('Namespace')
    submit = wtforms.SubmitField(
        '<span class="glyphicon glyphicon-search"></span> Filter results',
        widget=button_widget)
    ignore_labels = ['submit']
    css_classes = {'submit': 'btn btn-primary'}


class CommentForm(ReactorForm):
    body = wtforms.TextAreaField('Comment', validators=[
        wtforms.validators.Length(min=1),
        wtforms.validators.DataRequired()
    ])
    submit = wtforms.SubmitField('Comment', )
    ignore_labels = ['submit']
    css_classes = {'submit': 'btn btn-primary'}


class EmailChannelCreateForm(ReactorForm):
    email = wtforms.StringField(_('Email Address'),
                                filters=[strip_filter],
                                validators=[email_validator,
                                            unique_alert_email_validator,
                                            wtforms.validators.DataRequired()])
    submit = wtforms.SubmitField('Add email channel', )
    ignore_labels = ['submit']
    css_classes = {'submit': 'btn btn-primary'}


def gen_user_profile_form():
    class UserProfileForm(ReactorForm):
        email = wtforms.StringField(
            _('Email Address'),
            validators=[email_validator, wtforms.validators.DataRequired()])
        first_name = wtforms.StringField(_('First Name'))
        last_name = wtforms.StringField(_('Last Name'))
        company_name = wtforms.StringField(_('Company Name'))
        company_address = wtforms.TextAreaField(_('Company Address'))
        zip_code = wtforms.StringField(_('ZIP code'))
        city = wtforms.StringField(_('City'))
        notifications = wtforms.BooleanField('Account notifications',
                                             false_values=FALSE_VALUES)
        submit = wtforms.SubmitField(_('Update Account'))
        ignore_labels = ['submit']
        css_classes = {'submit': 'btn btn-primary'}

    return UserProfileForm


class PurgeAppForm(ReactorForm):
    resource_id = wtforms.HiddenField(
        'App Id',
        validators=[wtforms.validators.DataRequired()])
    days = wtforms.IntegerField(
        'Days',
        validators=[wtforms.validators.DataRequired()])
    password = wtforms.PasswordField(
        'Admin Password',
        validators=[old_password_validator, wtforms.validators.DataRequired()])
    submit = wtforms.SubmitField(_('Purge Data'))
    ignore_labels = ['submit']
    css_classes = {'submit': 'btn btn-primary'}


class IntegrationRepoForm(ReactorForm):
    host_name = wtforms.StringField("Service Host", default='')
    user_name = wtforms.StringField(
        "User Name",
        filters=[strip_filter],
        validators=[wtforms.validators.DataRequired(),
                    wtforms.validators.Length(min=1)])
    repo_name = wtforms.StringField(
        "Repo Name",
        filters=[strip_filter],
        validators=[wtforms.validators.DataRequired(),
                    wtforms.validators.Length(min=1)])


class IntegrationBitbucketForm(IntegrationRepoForm):
    host_name = wtforms.StringField("Service Host",
                                    default='https://bitbucket.org')

    def validate_user_name(self, field):
        try:
            request = pyramid.threadlocal.get_current_request()
            client = BitbucketIntegration.create_client(
                request,
                self.user_name.data,
                self.repo_name.data)
            client.get_assignees()
        except IntegrationException as e:
            raise wtforms.validators.ValidationError(str(e))


class IntegrationGithubForm(IntegrationRepoForm):
    host_name = wtforms.StringField("Service Host",
                                    default='https://github.com')

    def validate_user_name(self, field):
        try:
            request = pyramid.threadlocal.get_current_request()
            client = GithubIntegration.create_client(
                request,
                self.user_name.data,
                self.repo_name.data)
            client.get_assignees()
        except IntegrationException as e:
            raise wtforms.validators.ValidationError(str(e))
            raise wtforms.validators.ValidationError(str(e))


def filter_rooms(data):
    if data is not None:
        rooms = data.split(',')
        return ','.join([r.strip() for r in rooms])


class IntegrationCampfireForm(ReactorForm):
    account = wtforms.StringField(
        'Account',
        filters=[strip_filter],
        validators=[wtforms.validators.DataRequired()])
    api_token = wtforms.StringField(
        'Api Token',
        filters=[strip_filter],
        validators=[wtforms.validators.DataRequired()])
    rooms = wtforms.StringField('Room ID list', filters=[filter_rooms])

    def validate_api_token(self, field):
        try:
            client = CampfireIntegration.create_client(self.api_token.data,
                                                       self.account.data)
            client.get_account()
        except IntegrationException as e:
            raise wtforms.validators.ValidationError(str(e))

    def validate_rooms(self, field):
        if not field.data:
            return
        client = CampfireIntegration.create_client(self.api_token.data,
                                                   self.account.data)

        try:
            room_list = [r['id'] for r in client.get_rooms()]
        except IntegrationException as e:
            raise wtforms.validators.ValidationError(str(e))

        rooms = field.data.split(',')
        if len(rooms) > 3:
            msg = 'You can use up to 3 room ids'
            raise wtforms.validators.ValidationError(msg)
        if rooms:
            for room_id in rooms:
                if int(room_id) not in room_list:
                    msg = "Room %s doesn't exist"
                    raise wtforms.validators.ValidationError(msg % room_id)
                if not room_id.strip().isdigit():
                    msg = 'You must use only integers for room ids'
                    raise wtforms.validators.ValidationError(msg)

    submit = wtforms.SubmitField(_('Connect to Campfire'))
    ignore_labels = ['submit']
    css_classes = {'submit': 'btn btn-primary'}


def filter_rooms(data):
    if data is not None:
        rooms = data.split(',')
        return ','.join([r.strip() for r in rooms])


class IntegrationHipchatForm(ReactorForm):
    api_token = wtforms.StringField(
        'Api Token',
        filters=[strip_filter],
        validators=[wtforms.validators.DataRequired()])
    rooms = wtforms.StringField(
        'Room ID list',
        filters=[filter_rooms],
        validators=[wtforms.validators.DataRequired()])

    def validate_rooms(self, field):
        if not field.data:
            return
        client = HipchatIntegration.create_client(self.api_token.data)
        rooms = field.data.split(',')
        if len(rooms) > 3:
            msg = 'You can use up to 3 room ids'
            raise wtforms.validators.ValidationError(msg)
        if rooms:
            for room_id in rooms:
                if not room_id.strip().isdigit():
                    msg = 'You must use only integers for room ids'
                    raise wtforms.validators.ValidationError(msg)
                try:
                    client.send({
                        "message_format": 'text',
                        "message": "testing for room existence",
                        "from": "AppEnlight",
                        "room_id": room_id,
                        "color": "green"
                    })
                except IntegrationException as exc:
                    msg = 'Room id: %s exception: %s'
                    raise wtforms.validators.ValidationError(msg % (room_id,
                                                                    exc))


class IntegrationFlowdockForm(ReactorForm):
    api_token = wtforms.StringField('API Token',
                                    filters=[strip_filter],
                                    validators=[
                                        wtforms.validators.DataRequired()
                                    ], )

    def validate_api_token(self, field):
        try:
            client = FlowdockIntegration.create_client(self.api_token.data)
            registry = pyramid.threadlocal.get_current_registry()
            payload = {
                "source": registry.settings['mailing.from_name'],
                "from_address": registry.settings['mailing.from_email'],
                "subject": "Integration test",
                "content": "If you can see this it was successful",
                "tags": ["appenlight"],
                "link": registry.settings['mailing.app_url']
            }
            client.send_to_inbox(payload)
        except IntegrationException as e:
            raise wtforms.validators.ValidationError(str(e))


class IntegrationSlackForm(ReactorForm):
    webhook_url = wtforms.StringField(
        'Reports webhook',
        filters=[strip_filter],
        validators=[wtforms.validators.DataRequired()])

    def validate_webhook_url(self, field):
        registry = pyramid.threadlocal.get_current_registry()
        client = SlackIntegration.create_client(field.data)
        link = "<%s|%s>" % (registry.settings['mailing.app_url'],
                            registry.settings['mailing.from_name'])
        test_data = {
            "username": "AppEnlight",
            "icon_emoji": ":fire:",
            "attachments": [
                {"fallback": "Testing integration channel: %s" % link,
                 "pretext": "Testing integration channel:  %s" % link,
                 "color": "good",
                 "fields": [
                     {
                         "title": "Status",
                         "value": "Integration is working fine",
                         "short": False
                     }
                 ]}
            ]
        }
        try:
            client.make_request(data=test_data)
        except IntegrationException as exc:
            raise wtforms.validators.ValidationError(str(exc))


class IntegrationWebhooksForm(ReactorForm):
    reports_webhook = wtforms.StringField(
        'Reports webhook',
        filters=[strip_filter],
        validators=[wtforms.validators.DataRequired()])
    alerts_webhook = wtforms.StringField(
        'Alerts webhook',
        filters=[strip_filter],
        validators=[wtforms.validators.DataRequired()])
    submit = wtforms.SubmitField(_('Setup webhooks'))
    ignore_labels = ['submit']
    css_classes = {'submit': 'btn btn-primary'}


class IntegrationJiraForm(ReactorForm):
    host_name = wtforms.StringField(
        'Server URL',
        filters=[strip_filter],
        validators=[wtforms.validators.DataRequired()])
    user_name = wtforms.StringField(
        'Username',
        filters=[strip_filter],
        validators=[wtforms.validators.DataRequired()])
    password = wtforms.PasswordField(
        'Password',
        filters=[strip_filter],
        validators=[wtforms.validators.DataRequired()])
    project = wtforms.StringField(
        'Project key',
        filters=[uppercase_filter, strip_filter],
        validators=[wtforms.validators.DataRequired()])

    def validate_project(self, field):
        if not field.data:
            return
        try:
            client = JiraClient(self.user_name.data,
                                self.password.data,
                                self.host_name.data,
                                self.project.data)
        except Exception as exc:
            raise wtforms.validators.ValidationError(str(exc))

        room_list = [r.key.upper() for r in client.get_projects()]
        if field.data.upper() not in room_list:
            msg = "Project %s doesn\t exist in your Jira Instance"
            raise wtforms.validators.ValidationError(msg % field.data)


def get_deletion_form(resource):
    class F(ReactorForm):
        application_name = wtforms.StringField(
            'Application Name',
            filters=[strip_filter],
            validators=[wtforms.validators.AnyOf([resource.resource_name])])
        resource_id = wtforms.HiddenField(default=resource.resource_id)
        submit = wtforms.SubmitField(_('Delete my application'))
        ignore_labels = ['submit']
        css_classes = {'submit': 'btn btn-danger'}

    return F


class ChangeApplicationOwnerForm(ReactorForm):
    password = wtforms.PasswordField(
        'Password',
        filters=[strip_filter],
        validators=[old_password_validator,
                    wtforms.validators.DataRequired()])

    user_name = wtforms.StringField(
        'New owners username',
        filters=[strip_filter],
        validators=[found_username_validator,
                    wtforms.validators.DataRequired()])
    submit = wtforms.SubmitField(_('Transfer ownership of application'))
    ignore_labels = ['submit']
    css_classes = {'submit': 'btn btn-danger'}


def default_filename():
    return 'Invoice %s' % datetime.datetime.utcnow().strftime('%Y/%m')


class FileUploadForm(ReactorForm):
    title = wtforms.StringField('File Title',
                                default=default_filename,
                                validators=[wtforms.validators.DataRequired()])
    file = wtforms.FileField('File')

    def validate_file(self, field):
        if not hasattr(field.data, 'file'):
            raise wtforms.ValidationError('File is missing')

    submit = wtforms.SubmitField(_('Upload'))


def get_partition_deletion_form(es_indices, pg_indices):
    class F(ReactorForm):
        es_index = wtforms.SelectMultipleField('Elasticsearch',
                                               choices=[(ix, '') for ix in
                                                        es_indices])
        pg_index = wtforms.SelectMultipleField('pg',
                                               choices=[(ix, '') for ix in
                                                        pg_indices])
        confirm = wtforms.TextField('Confirm',
                                    filters=[uppercase_filter, strip_filter],
                                    validators=[
                                        wtforms.validators.AnyOf(['CONFIRM']),
                                        wtforms.validators.DataRequired()])
        ignore_labels = ['submit']
        css_classes = {'submit': 'btn btn-danger'}

    return F


class GroupCreateForm(ReactorForm):
    group_name = wtforms.StringField(
        _('Group Name'),
        filters=[strip_filter],
        validators=[
            wtforms.validators.Length(min=2, max=50),
            unique_groupname_validator,
            wtforms.validators.DataRequired()
        ])
    description = wtforms.StringField(_('Group description'))


time_choices = [(k, v['label'],) for k, v in h.time_deltas.items()]


class AuthTokenCreateForm(ReactorForm):
    description = wtforms.StringField(_('Token description'))
    expires = wtforms.SelectField('Expires',
                                  coerce=lambda x: x,
                                  choices=time_choices,
                                  validators=[wtforms.validators.Optional()])
