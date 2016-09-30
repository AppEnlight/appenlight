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
// # AppEnlight Enterprise Edition, including its added features, Support
// # services, and proprietary license terms, please see
// # https://rhodecode.com/licenses/

angular.module('appenlight.controllers')
    .controller('ApplicationsUpdateController', ApplicationsUpdateController)

ApplicationsUpdateController.$inject = ['$state', 'applicationsNoIdResource', 'applicationsResource', 'applicationsPropertyResource', 'stateHolder'];

function ApplicationsUpdateController($state, applicationsNoIdResource, applicationsResource, applicationsPropertyResource, stateHolder) {
    'use strict';
    console.debug('ApplicationsUpdateController');
    var vm = this;
    vm.loading = {application: false};

    vm.groupingOptions = [
        ['url_type', 'Error Type + location'],
        ['url_traceback', 'Traceback + location'],
        ['traceback_server', 'Traceback + Server'],
    ];

    var resourceId = $state.params.resourceId;


    var options = {};

    vm.momentJs = moment;
    
    vm.formTransferModel = {password:''};

    // set initial data

    if (resourceId === 'new') {
        vm.resource = {
            resource_id: null,
            slow_report_threshold: 10,
            error_report_threshold: 10,
            allow_permanent_storage: true,
            default_grouping: vm.groupingOptions[1][0]
        };
    }
    else {
        vm.loading.application = true;
        vm.resource = applicationsResource.get({
            'resourceId': resourceId
        }, function (data) {
            vm.loading.application = false;
        });
    }


    vm.updateBasicForm = function () {
        vm.loading.application = true;
        if (vm.resource.resource_id === null) {
            applicationsNoIdResource.save(null, vm.resource, function (data) {
                stateHolder.AeUser.addApplication(data);
                $state.go('applications.update', {resourceId: data.resource_id});
                setServerValidation(vm.BasicForm);
            }, function (response) {
                if (response.status == 422) {
                    setServerValidation(vm.BasicForm, response.data);
                }
                vm.loading.application = false;
                console.log(vm.BasicForm);
            });
        }
        else {
            applicationsResource.update({resourceId: vm.resource.resource_id},
                vm.resource, function (data) {
                    vm.resource = data;
                    vm.loading.application = false;
                    setServerValidation(vm.BasicForm);
                }, function (response) {
                    if (response.status == 422) {
                        setServerValidation(vm.BasicForm, response.data);
                    }
                    vm.loading.application = false;
                });
        }
    };

    vm.addRule = function () {
        console.log('addrule');
        applicationsPropertyResource.save({
                resourceId: vm.resource.resource_id,
                key: 'postprocessing_rules'
            }, null,
            function (data) {
                vm.resource.postprocessing_rules.push(data);
            }
        );
    };

    vm.regenerateAPIKeys = function(){
        vm.loading.application = true;
        applicationsPropertyResource.save({
                resourceId: vm.resource.resource_id,
                key: 'api_key'
            }, {password: vm.regenerateAPIKeysPassword},
            function (data) {
                vm.resource = data;
                vm.loading.application = false;
                vm.regenerateAPIKeysPassword = '';
                setServerValidation(vm.regenerateAPIKeysForm);
            },
            function (response) {
                if (response.status == 422) {
                    setServerValidation(vm.regenerateAPIKeysForm, response.data);
                    console.log(response.data);
                }
                vm.loading.application = false;
            }
        )
    };

    vm.deleteApplication = function(){
        vm.loading.application = true;
        applicationsPropertyResource.update({
                resourceId: vm.resource.resource_id,
                key: 'delete_resource'
            }, vm.formDeleteModel,
            function (data) {
                stateHolder.AeUser.removeApplicationById(vm.resource.resource_id);
                $state.go('applications.list');
            },
            function (response) {
                if (response.status == 422) {
                    setServerValidation(vm.formDelete, response.data);
                    console.log(response.data);
                }
                vm.loading.application = false;
            }
        );
    };

    vm.transferApplication = function(){
        vm.loading.application = true;
        applicationsPropertyResource.update({
                resourceId: vm.resource.resource_id,
                key: 'owner'
            }, vm.formTransferModel,
            function (data) {
                $state.go('applications.list');
            },
            function (response) {
                if (response.status == 422) {
                    setServerValidation(vm.formTransfer, response.data);
                    console.log(response.data);
                }
                vm.loading.application = false;
            }
        )
    }

}
