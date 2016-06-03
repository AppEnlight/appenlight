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
