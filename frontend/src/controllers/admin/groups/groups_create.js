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

angular.module('appenlight.controllers').controller('AdminGroupsCreateController', AdminGroupsCreateController);

AdminGroupsCreateController.$inject = ['$state', 'groupsResource', 'groupsPropertyResource', 'sectionViewResource', 'AeConfig'];

function AdminGroupsCreateController($state, groupsResource, groupsPropertyResource, sectionViewResource, AeConfig) {
    console.debug('AdminGroupsCreateController');
    var vm = this;
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

    }
    else {
        var groupId = null;
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
        }
        else {
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
