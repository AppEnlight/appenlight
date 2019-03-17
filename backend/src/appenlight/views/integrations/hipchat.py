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
from datetime import datetime

from appenlight.models import DBSession
from appenlight.models.integrations.hipchat import HipchatIntegration
from pyramid.httpexceptions import HTTPUnprocessableEntity
from pyramid.view import view_config
from appenlight import forms

from webob.multidict import MultiDict

log = logging.getLogger(__name__)

from . import IntegrationView


class HipchatView(IntegrationView):
    @view_config(
        route_name="integrations_id",
        match_param=["action=info", "integration=hipchat"],
        renderer="json",
    )
    def get_info(self):
        pass

    @view_config(
        route_name="integrations_id",
        match_param=["action=setup", "integration=hipchat"],
        renderer="json",
        permission="edit",
    )
    def setup(self):
        """
        Validates and creates integration between application and hipchat
        """
        resource = self.request.context.resource
        self.create_missing_channel(resource, "hipchat")
        form = forms.IntegrationHipchatForm(
            MultiDict(self.request.safe_json_body or {}),
            csrf_context=self.request,
            **self.integration_config
        )
        if self.request.method == "POST" and form.validate():
            integration_config = {
                "api_token": form.api_token.data,
                "rooms": form.rooms.data,
            }
            if not self.integration:
                # add new integration
                self.integration = HipchatIntegration(modified_date=datetime.utcnow())
                self.request.session.flash("Integration added")
                resource.integrations.append(self.integration)
            else:
                self.request.session.flash("Integration updated")
            self.integration.config = integration_config
            DBSession.flush()
            self.create_missing_channel(resource, "hipchat")
            return integration_config
        elif self.request.method == "POST":
            return HTTPUnprocessableEntity(body=form.errors_json)
        return self.integration_config
