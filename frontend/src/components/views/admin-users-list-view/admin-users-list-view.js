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

angular.module('appenlight.components.adminUsersListView', [])
    .component('adminUsersListView', {
        templateUrl: 'components/views/admin-users-list-view/admin-users-list-view.html',
        controller: AdminUserListViewController
    });

AdminUserListViewController.$inject = ['usersResource'];

function AdminUserListViewController(usersResource) {
    console.debug('AdminUsersController');
    var vm = this;
    vm.$onInit = function () {
        vm.loading = {users: true};

        vm.users = usersResource.query({}, function (data) {
            vm.loading = {users: false};
            vm.activeUsers = _.reduce(vm.users, function (memo, val) {
                if (val.status == 1) {
                    return memo + 1;
                }
                return memo;
            }, 0);
            console.log(vm.users);
        });
    }

    vm.removeUser = function (user) {
        usersResource.remove({userId: user.id}, function (data, responseHeaders) {
            console.log('x',data, responseHeaders());
            if (data) {
                var index = vm.users.indexOf(user);
                if (index !== -1) {
                    vm.users.splice(index, 1);
                    vm.activeUsers -= 1;
                }
            }
        });
    }
};
