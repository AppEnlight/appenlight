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

angular.module('appenlight.controllers')
    .controller('ApplicationPermissionsController', ApplicationPermissionsController);

ApplicationPermissionsController.$inject = ['sectionViewResource',
    'applicationsPropertyResource', 'groupsResource']


function ApplicationPermissionsController(sectionViewResource, applicationsPropertyResource , groupsResource) {
    var vm = this;
    vm.form = {
        autocompleteUser: '',
        selectedGroup: null,
        selectedUserPermissions: {},
        selectedGroupPermissions: {}
    }
    vm.possibleGroups = groupsResource.query(null, function(){
        if (vm.possibleGroups.length > 0){
            vm.form.selectedGroup = vm.possibleGroups[0].id;
        }
    });
    console.log('g', vm.possibleGroups);
    vm.possibleUsers = [];
    _.each(vm.resource.possible_permissions, function (perm) {
        vm.form.selectedUserPermissions[perm] = false;
        vm.form.selectedGroupPermissions[perm] = false;
    });

    /**
     * Converts the permission list into {user, permission_list objects}
     * for rendering in templates
     * **/
    var tmpObj = {
        user: {},
        group: {}
    };
    _.each(vm.currentPermissions, function (perm) {
        console.log(perm);
        if (perm.type == 'user') {
            if (typeof tmpObj[perm.type][perm.user_name] === 'undefined') {
                tmpObj[perm.type][perm.user_name] = {
                    self: perm,
                    permissions: []
                }
            }
            if (tmpObj[perm.type][perm.user_name].permissions.indexOf(perm.perm_name) === -1) {
                tmpObj[perm.type][perm.user_name].permissions.push(perm.perm_name);
            }
        }
        else {
            if (typeof tmpObj[perm.type][perm.group_name] === 'undefined') {
                tmpObj[perm.type][perm.group_name] = {
                    self: perm,
                    permissions: []
                }
            }
            if (tmpObj[perm.type][perm.group_name].permissions.indexOf(perm.perm_name) === -1) {
                tmpObj[perm.type][perm.group_name].permissions.push(perm.perm_name);
            }

        }
    });
    vm.currentPermissions = {
        user: _.values(tmpObj.user),
        group: _.values(tmpObj.group),
    };

    console.log('test', tmpObj, vm.currentPermissions);

    vm.searchUsers = function (searchPhrase) {
        console.log('SEARCHING');
        vm.searchingUsers = true;
        return sectionViewResource.query({
            section: 'users_section',
            view: 'search_users',
            'user_name': searchPhrase
        }).$promise.then(function (data) {
                vm.searchingUsers = false;
                return _.map(data, function (item) {
                    return item;
                });
            });
    };


    vm.setGroupPermission = function(){
        var POSTObj = {
            'group_id': vm.form.selectedGroup,
            'permissions': []
        };
        for (var key in vm.form.selectedGroupPermissions) {
            if (vm.form.selectedGroupPermissions[key]) {
                POSTObj.permissions.push(key)
            }
        }
        applicationsPropertyResource.save({
                key: 'group_permissions',
                resourceId: vm.resource.resource_id
            }, POSTObj,
            function (data) {
                var found_row = false;
                _.each(vm.currentPermissions.group, function (perm) {
                    if (perm.self.group_id == data.group.id) {
                        perm['permissions'] = data['permissions'];
                        found_row = true;
                    }
                });
                if (!found_row) {
                    data.self = data.group;
                    // normalize data format
                    data.self.group_id = data.self.id;
                    vm.currentPermissions.group.push(data);
                }
            });

    }


    vm.setUserPermission = function () {
        console.log('set permissions');
        var POSTObj = {
            'user_name': vm.form.autocompleteUser,
            'permissions': []
        };
        for (var key in vm.form.selectedUserPermissions) {
            if (vm.form.selectedUserPermissions[key]) {
                POSTObj.permissions.push(key)
            }
        }
        applicationsPropertyResource.save({
                key: 'user_permissions',
                resourceId: vm.resource.resource_id
            }, POSTObj,
            function (data) {
                var found_row = false;
                _.each(vm.currentPermissions.user, function (perm) {
                    if (perm.self.user_name == data['user_name']) {
                        perm['permissions'] = data['permissions'];
                        found_row = true;
                    }
                });
                if (!found_row) {
                    data.self = data;
                    vm.currentPermissions.user.push(data);
                }
            });
    }

    vm.removeUserPermission = function (perm_name, curr_perm) {
        console.log(perm_name);
        console.log(curr_perm);
        var POSTObj = {
            key: 'user_permissions',
            user_name: curr_perm.self.user_name,
            permissions: [perm_name],
            resourceId: vm.resource.resource_id
        }
        applicationsPropertyResource.delete(POSTObj, function (data) {
            _.each(vm.currentPermissions.user, function (perm) {
                if (perm.self.user_name == data['user_name']) {
                    perm['permissions'] = data['permissions']
                }
            });
        });
    }

    vm.removeGroupPermission = function (perm_name, curr_perm) {
        console.log('g', curr_perm);
        var POSTObj = {
            key: 'group_permissions',
            group_id: curr_perm.self.group_id,
            permissions: [perm_name],
            resourceId: vm.resource.resource_id
        }
        applicationsPropertyResource.delete(POSTObj, function (data) {
            _.each(vm.currentPermissions.group, function (perm) {
                if (perm.self.group_id == data.group.id) {
                    perm['permissions'] = data['permissions']
                }
            });
        });
    }
}

angular.module('appenlight.directives.permissionsForm',[])
    .directive('permissionsForm', function () {
        return {
            "restrict": "E",
            "controller": "ApplicationPermissionsController",
            controllerAs: 'permissions',
            bindToController: true,
            scope: {
                currentPermissions: '=',
                possiblePermissions: '=',
                resource: '='
            },
            templateUrl: 'directives/permissions/permissions.html'
        }
    })
