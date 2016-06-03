// # Copyright (C) 2010-2016  RhodeCode GmbH
// #
// # This program is free software: you can redistribute it and/or modify
// # it under the terms of the GNU Affero General Public License, version 3
// # (only), as published by the Free Software Foundation.
// #
// # This program is distributed in the hope that it will be useful,
// # but WITHOUT ANY WARRANTY; without even the implied warranty of
// # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// # GNU General Public License for more details.
// #
// # You should have received a copy of the GNU Affero General Public License
// # along with this program.  If not, see <http://www.gnu.org/licenses/>.
// #
// # This program is dual-licensed. If you wish to learn more about the
// # App Enlight Enterprise Edition, including its added features, Support
// # services, and proprietary license terms, please see
// # https://rhodecode.com/licenses/

angular.module('appenlight.controllers')
    .controller('BitbucketIntegrationCtrl', BitbucketIntegrationCtrl)

BitbucketIntegrationCtrl.$inject = ['$uibModalInstance', '$state', 'report', 'integrationName', 'integrationResource'];

function BitbucketIntegrationCtrl($uibModalInstance, $state, report, integrationName, integrationResource) {
    var vm = this;
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
        $state.href('report.view_detail', {groupId:report.group_id, reportId:report.id}, {absolute:true})
    };

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
                }
                else {
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
                }
                else {
                    vm.error_messages = ['There was a problem processing your request'];
                }
            });
    };
    vm.cancel = function () {
        $uibModalInstance.dismiss('cancel');
    };
    vm.fetchInfo();
}
