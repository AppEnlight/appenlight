// Copyright 2010 - 2017 RhodeCode GmbH and the AppEnlight project authors
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//   http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

angular.module('appenlight.components.adminApplicationsListView', [])
    .component('adminApplicationsListView', {
        templateUrl: 'components/views/admin-applications-list-view/admin-applications-list-view.html',
        controller: AdminApplicationsListController
    });

AdminApplicationsListController.$inject = ['applicationsResource'];

function AdminApplicationsListController(applicationsResource) {
    console.debug('AdminApplicationsListController');
    var vm = this;
    vm.$onInit = function () {
        vm.loading = {applications: true};

        vm.applications = applicationsResource.query({
            root_list: true,
            resource_type: 'application'
        }, function (data) {
            vm.loading = {applications: false};
        });
    }
};
