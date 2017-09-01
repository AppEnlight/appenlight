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

angular.module('appenlight.controllers').controller('AssignReportCtrl', AssignReportCtrl);
AssignReportCtrl.$inject = ['$uibModalInstance', 'reportGroupPropertyResource', 'report'];

function AssignReportCtrl($uibModalInstance, reportGroupPropertyResource, report) {
    var vm = this;
    vm.loading = true;
    vm.assignedUsers = [];
    vm.unAssignedUsers = [];
    vm.report = report;
    vm.fetchAssignments = function () {
        reportGroupPropertyResource.get({
                groupId: vm.report.group_id,
                key: 'assigned_users'
            }, null,
            function (data) {
                vm.assignedUsers = data.assigned;
                vm.unAssignedUsers = data.unassigned;
                vm.loading = false;
            });
    }

    vm.reassignUser = function (user) {
        var is_assigned = vm.assignedUsers.indexOf(user);
        if (is_assigned != -1) {
            vm.assignedUsers.splice(is_assigned, 1);
            vm.unAssignedUsers.push(user);
            return
        }
        var is_unassigned = vm.unAssignedUsers.indexOf(user);
        if (is_unassigned != -1) {
            vm.unAssignedUsers.splice(is_unassigned, 1);
            vm.assignedUsers.push(user);
            return
        }
    }
    vm.updateAssignments = function () {
        var post = {'unassigned': [], 'assigned': []};
        _.each(vm.assignedUsers, function (u) {
            post['assigned'].push(u.user_name)
        });
        _.each(vm.unAssignedUsers, function (u) {
            post['unassigned'].push(u.user_name)
        });
        vm.loading = true;
        reportGroupPropertyResource.update({
                groupId: vm.report.group_id,
                key: 'assigned_users'
            }, post,
            function (data) {
                vm.loading = false;
                $uibModalInstance.close(vm.report);
            });
    };


    vm.ok = function () {
        vm.updateAssignments();
    };

    vm.cancel = function () {
        $uibModalInstance.dismiss('cancel');
    };

    vm.fetchAssignments();

}
