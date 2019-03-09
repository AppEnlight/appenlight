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

angular.module('appenlight.controllers')
    .controller('BitbucketIntegrationCtrl', BitbucketIntegrationCtrl)

BitbucketIntegrationCtrl.$inject = ['$uibModalInstance', '$state', 'report', 'integrationName', 'integrationResource'];

function BitbucketIntegrationCtrl($uibModalInstance, $state, report, integrationName, integrationResource) {
    var vm = this;
    vm.$onInit = function () {
        vm.loading = true;
        vm.assignees = [];
        vm.report = report;
        vm.integrationName = integrationName;
        vm.statuses = [];
        vm.priorities = [];
        vm.error_messages = [];
        vm.form = {
            content: '\n' +
                'Issue created for report: ' +
                $state.href('report.view_detail', {groupId: report.group_id, reportId: report.id}, {absolute: true})
        };
        vm.fetchInfo();
    }
    vm.fetchInfo = function () {
        integrationResource.get({
                resourceId: vm.report.resource_id,
                action: 'info',
                integration: vm.integrationName
            }, null,
            function (data) {
                vm.loading = false;
                if (data.error_messages) {
                    vm.error_messages = data.error_messages;
                }
                vm.assignees = data.assignees;
                vm.priorities = data.priorities;
                vm.form.responsible = vm.assignees[0];
                vm.form.priority = vm.priorities[0];
            }, function (error_data) {
                if (error_data.data.error_messages) {
                    vm.error_messages = error_data.data.error_messages;
                } else {
                    vm.error_messages = ['There was a problem processing your request'];
                }
            });
    };
    vm.ok = function () {
        vm.loading = true;
        vm.form.group_id = vm.report.group_id;
        integrationResource.save({
                resourceId: vm.report.resource_id,
                action: 'create-issue',
                integration: vm.integrationName
            }, vm.form,
            function (data) {
                vm.loading = false;
                if (data.error_messages) {
                    vm.error_messages = data.error_messages;
                }
                if (data !== false) {
                    $uibModalInstance.dismiss('success');
                }
            }, function (error_data) {
                if (error_data.data.error_messages) {
                    vm.error_messages = error_data.data.error_messages;
                } else {
                    vm.error_messages = ['There was a problem processing your request'];
                }
            });
    };
    vm.cancel = function () {
        $uibModalInstance.dismiss('cancel');
    };
}
