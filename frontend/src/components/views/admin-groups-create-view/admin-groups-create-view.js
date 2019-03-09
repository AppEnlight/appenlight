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

angular.module('appenlight.components.adminGroupsCreateView', [])
    .component('adminGroupsCreateView', {
        templateUrl: 'components/views/admin-groups-create-view/admin-groups-create-view.html',
        controller: AdminGroupsCreateViewController
    });

AdminGroupsCreateViewController.$inject = ['$state', 'groupsResource', 'groupsPropertyResource', 'sectionViewResource'];

function AdminGroupsCreateViewController($state, groupsResource, groupsPropertyResource, sectionViewResource) {
    console.debug('AdminGroupsCreateController');
    var vm = this;
    vm.$onInit = function () {
        vm.$state = $state;
        vm.loading = {
            group: false,
            resource_permissions: false,
            users: false
        };

        vm.form = {
            autocompleteUser: '',
        }


        if (typeof $state.params.groupId !== 'undefined') {
            vm.loading.group = true;
            var groupId = $state.params.groupId;
            vm.group = groupsResource.get({groupId: groupId}, function (data) {
                vm.loading.group = false;
            });

            vm.resource_permissions = groupsPropertyResource.query(
                {groupId: groupId, key: 'resource_permissions'}, function (data) {
                    vm.loading.resource_permissions = false;
                    var tmpObj = {
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

            vm.users = groupsPropertyResource.query(
                {groupId: groupId, key: 'users'}, function (data) {
                    vm.loading.users = false;
                }, function () {
                    vm.loading.users = false;
                });

        } else {
            var groupId = null;
        }

    }

    var formResponse = function (response) {
        if (response.status === 422) {
            setServerValidation(vm.groupForm, response.data);
        }
        vm.loading.group = false;
    };

    vm.createGroup = function () {
        vm.loading.group = true;
        if (groupId) {
            groupsResource.update({groupId: vm.group.id}, vm.group, function (data) {
                setServerValidation(vm.groupForm);
                vm.loading.group = false;
            }, formResponse);
        } else {
            groupsResource.save(vm.group, function (data) {
                $state.go('admin.group.update', {groupId: data.id});
            }, formResponse);
        }
    };

    vm.removeUser = function (user) {
        groupsPropertyResource.delete(
            {groupId: groupId, key: 'users', user_name: user.user_name},
            function (data) {
                vm.loading.users = false;
                vm.users = _.filter(vm.users, function (item) {
                    return item != user;
                });
            }, function () {
                vm.loading.users = false;
            });
    };

    vm.addUser = function () {
        groupsPropertyResource.save(
            {groupId: groupId, key: 'users'},
            {user_name: vm.form.autocompleteUser},
            function (data) {
                vm.loading.users = false;
                vm.users.push(data);
                vm.form.autocompleteUser = '';
            }, function () {
                vm.loading.users = false;
            });
    }

    vm.searchUsers = function (searchPhrase) {
        console.log(searchPhrase);
        return sectionViewResource.query({
            section: 'users_section',
            view: 'search_users',
            'user_name': searchPhrase
        }).$promise.then(function (data) {
            return _.map(data, function (item) {
                return item.user;
            });
        });
    }
};
