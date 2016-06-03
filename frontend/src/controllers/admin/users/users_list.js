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

angular.module('appenlight.controllers').controller('AdminUsersController', AdminUsersController);

AdminUsersController.$inject = ['usersResource'];

function AdminUsersController(usersResource) {
    console.debug('AdminUsersController');
    var vm = this;
    vm.loading = {users: true};

    vm.users = usersResource.query({}, function (data) {
        vm.loading = {users: false};
        vm.activeUsers = _.reduce(vm.users, function(memo, val){
            if (val.status == 1){
                return memo + 1;
            }
            return memo;
        }, 0);
        console.log(vm.users);
    });


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
