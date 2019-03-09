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

angular.module('appenlight.components.applicationsListView', [])
    .component('applicationsListView', {
        templateUrl: 'components/views/applications-list-view/applications-list-view.html',
        controller: ApplicationsListViewController
    });

ApplicationsListViewController.$inject = ['$state', 'applicationsResource'];

function ApplicationsListViewController($state, applicationsResource) {
    console.debug('ApplicationsListController');
    var vm = this;
    vm.$onInit = function () {
        vm.$state = $state;
        vm.loading = {applications: true};
        vm.applications = applicationsResource.query(null, function () {
            vm.loading.applications = false;
        });
    }
}
