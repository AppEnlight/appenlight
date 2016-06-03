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
# App Enlight Enterprise Edition, including its added features, Support
# services, and proprietary license terms, please see
# https://rhodecode.com/licenses/

from appenlight.models import DBSession
from appenlight.models.integrations.flowdock import FlowdockIntegration
from pyramid.httpexceptions import HTTPUnprocessableEntity
from pyramid.view import view_config
from appenlight import forms
import logging
from datetime import datetime
from webob.multidict import MultiDict

log = logging.getLogger(__name__)

from . import IntegrationView


class FlowdockView(IntegrationView):
    @view_config(route_name='integrations_id',
                 match_param=['action=info', 'integration=flowdock'],
                 renderer='json')
    def get_info(self):
        pass

    @view_config(route_name='integrations_id',
                 match_param=['action=setup', 'integration=flowdock'],
                 renderer='json',
                 permission='edit')
    def setup(self):
        """
        Validates and creates integration between application and flowdock
        """
        resource = self.request.context.resource
        self.create_missing_channel(resource, 'flowdock')

        form = forms.IntegrationFlowdockForm(
            MultiDict(self.request.safe_json_body or {}),
            csrf_context=self.request, **self.integration_config)
        if self.request.method == 'POST' and form.validate():
            integration_config = {
                'api_token': form.api_token.data,
            }
            if not self.integration:
                # add new integration
                self.integration = FlowdockIntegration(
                    modified_date=datetime.utcnow(),
                )
                self.request.session.flash('Integration added')
                resource.integrations.append(self.integration)
            else:
                self.request.session.flash('Integration updated')
            self.integration.config = integration_config
            DBSession.flush()
            self.create_missing_channel(resource, 'flowdock')
            return integration_config
        elif self.request.method == 'POST':
            return HTTPUnprocessableEntity(body=form.errors_json)
        return self.integration_config
