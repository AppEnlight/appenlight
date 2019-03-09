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

angular.module('appenlight.components.adminUsersCreateView', [])
    .component('adminUsersCreateView', {
        templateUrl: 'components/views/admin-users-create-view/admin-users-create-view.html',
        controller: AdminUsersCreateViewController
    });

AdminUsersCreateViewController.$inject = ['$state', 'usersResource', 'usersPropertyResource', 'sectionViewResource', 'AeConfig'];

function AdminUsersCreateViewController($state, usersResource, usersPropertyResource, sectionViewResource, AeConfig) {
    console.debug('AdminUsersCreateViewController');
    var vm = this;
    vm.$onInit = function () {
        vm.$state = $state;
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
                        if (typeof section[item.resource_id] == 'undefined') {
                            section[item.resource_id] = {
                                self: item,
                                permissions: []
                            }
                        }
                        section[item.resource_id].permissions.push(item.perm_name);

                    });
                    console.log(tmpObj)
                    vm.resourcePermissions = tmpObj;
                });

        } else {
            var userId = null;
            vm.user = {
                status: true
            }
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
        var userId = $state.params.userId;
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
