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

from appenlight.models import DBSession
from appenlight.models.integrations.slack import SlackIntegration, IntegrationException
from pyramid.httpexceptions import HTTPUnprocessableEntity
from pyramid.view import view_config
from appenlight import forms
from datetime import datetime
from webob.multidict import MultiDict

log = logging.getLogger(__name__)

from . import IntegrationView


class SlackView(IntegrationView):
    @view_config(
        route_name="integrations_id",
        match_param=["action=info", "integration=slack"],
        renderer="json",
    )
    def get_info(self):
        pass

    @view_config(
        route_name="integrations_id",
        match_param=["action=setup", "integration=slack"],
        renderer="json",
        permission="edit",
    )
    def setup(self):
        """
        Validates and creates integration between application and slack
        """
        resource = self.request.context.resource
        self.create_missing_channel(resource, "slack")
        form = forms.IntegrationSlackForm(
            MultiDict(self.request.safe_json_body or {}),
            csrf_context=self.request,
            **self.integration_config
        )

        if self.request.method == "POST" and form.validate():
            integration_config = {"webhook_url": form.webhook_url.data}
            if not self.integration:
                # add new integration
                self.integration = SlackIntegration(modified_date=datetime.utcnow())
                self.request.session.flash("Integration added")
                resource.integrations.append(self.integration)
            else:
                self.request.session.flash("Integration updated")
            self.integration.config = integration_config
            DBSession.flush()
            self.create_missing_channel(resource, "slack")
            return integration_config
        elif self.request.method == "POST":
            return HTTPUnprocessableEntity(body=form.errors_json)
        return self.integration_config
