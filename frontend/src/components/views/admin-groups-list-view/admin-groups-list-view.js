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

angular.module('appenlight.components.adminGroupsListView', [])
    .component('adminGroupsListView', {
        templateUrl: 'components/views/admin-groups-list-view/admin-groups-list-view.html',
        controller: AdminGroupsListViewController
    });

AdminGroupsListViewController.$inject = ['$state', 'groupsResource'];

function AdminGroupsListViewController($state, groupsResource) {
    console.debug('AdminGroupsListViewController');
    var vm = this;
    this.$onInit = function () {
        vm.$state = $state;
        vm.loading = {groups: true};

        vm.groups = groupsResource.query({}, function (data) {
            vm.loading = {groups: false};
            vm.activeUsers = _.reduce(vm.groups, function (memo, val) {
                if (val.status == 1) {
                    return memo + 1;
                }
                return memo;
            }, 0);
            console.log(vm.groups);
        });
    }

    vm.removeGroup = function (group) {
        groupsResource.remove({groupId: group.id}, function (data, responseHeaders) {
            console.log('x', data, responseHeaders());
            if (data) {
                var index = vm.groups.indexOf(group);
                if (index !== -1) {
                    vm.groups.splice(index, 1);
                    vm.activeGroups -= 1;
                }
            }
        });
    }
};
