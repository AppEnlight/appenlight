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

angular.module('appenlight.components.applicationsPurgeLogsView', [])
    .component('applicationsPurgeLogsView', {
        templateUrl: 'components/views/applications-purge-logs-view/applications-purge-logs-view.html',
        controller: applicationsPurgeLogsViewController
    });

applicationsPurgeLogsViewController.$inject = ['$state', 'applicationsResource', 'sectionViewResource', 'logsNoIdResource'];

function applicationsPurgeLogsViewController($state, applicationsResource, sectionViewResource, logsNoIdResource) {
    console.debug('applicationsPurgeLogsViewController');
    var vm = this;
    vm.$onInit = function () {
        vm.$state = $state;
        vm.loading = {applications: true};

        vm.namespace = null;
        vm.selectedResource = null;
        vm.commonNamespaces = [];

        vm.applications = applicationsResource.query({'type': 'update_reports'}, function () {
            vm.loading.applications = false;
            vm.selectedResource = vm.applications[0].resource_id;
            vm.getCommonKeys();
        });
    }

    /**
     * Fetches most commonly used tags in logs
     */
    vm.getCommonKeys = function () {
        sectionViewResource.get({
            section: 'logs_section',
            view: 'common_tags',
            resource: vm.selectedResource
        }, function (data) {
            vm.commonNamespaces = data['namespaces']
        });
    };

    vm.purgeLogs = function () {
        vm.loading.applications = true;
        logsNoIdResource.delete({
            resource: vm.selectedResource,
            namespace: vm.namespace
        }, function () {
            vm.loading.applications = false;
        });
    }
}
