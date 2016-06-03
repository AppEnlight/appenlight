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

angular.module('appenlight.controllers').controller('AdminUsersCreateController', AdminUsersCreateController);

AdminUsersCreateController.$inject = ['$state', 'usersResource', 'usersPropertyResource', 'sectionViewResource', 'AeConfig'];

function AdminUsersCreateController($state, usersResource, usersPropertyResource, sectionViewResource, AeConfig) {
    console.debug('AdminUsersCreateController');
    var vm = this;
    vm.loading = {user: false};


    if (typeof $state.params.userId !== 'undefined') {
        vm.loading.user = true;
        var userId = $state.params.userId;
        vm.user = usersResource.get({userId: userId}, function (data) {
            vm.loading.user = false;
            // cast to true for angular checkbox
            if (vm.user.status === 1) {
                vm.user.status = true;
            }
        });

        vm.resource_permissions = usersPropertyResource.query(
            {userId: userId, key: 'resource_permissions'}, function (data) {
                vm.loading.resource_permissions = false;
                var tmpObj = {
                    'user': {
                        'application': {},
                        'dashboard': {}
                    },
                    'group': {
                        'application': {},
                        'dashboard': {}
                    }
                };
                _.each(data, function (item) {
                    console.log(item);
                    var section = tmpObj[item.type][item.resource_type];
                    if (typeof section[item.resource_id] == 'undefined'){
                        section[item.resource_id] = {
                            self:item,
                            permissions: []
                        }
                    }
                    section[item.resource_id].permissions.push(item.perm_name);

                });
                console.log(tmpObj)
                vm.resourcePermissions = tmpObj;
            });

    }
    else {
        var userId = null;
        vm.user = {
            status: true
        }
    }

    var formResponse = function (response) {
        if (response.status == 422) {
            setServerValidation(vm.profileForm, response.data);
        }
        vm.loading.user = false;
    }

    vm.createUser = function () {
        vm.loading.user = true;
        console.log('updateProfile');
        if (userId) {
            usersResource.update({userId: vm.user.id}, vm.user, function (data) {
                setServerValidation(vm.profileForm);
                vm.loading.user = false;
            }, formResponse);
        }
        else {
            usersResource.save(vm.user, function (data) {
                $state.go('admin.user.update', {userId: data.id});
            }, formResponse);
        }
    }

    vm.generatePassword = function () {
        var length = 8;
        var charset = "abcdefghijklnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
        vm.gen_pass = "";
        for (var i = 0, n = charset.length; i < length; ++i) {
            vm.gen_pass += charset.charAt(Math.floor(Math.random() * n));
        }
        vm.user.user_password = '' + vm.gen_pass;
        console.log('x', vm.gen_pass);
    }

    vm.reloginUser = function () {
        sectionViewResource.get({
            section: 'admin_section', view: 'relogin_user',
            user_id: vm.user.id
        }, function () {
            window.location = AeConfig.urls.baseUrl;
        });

    }
};
