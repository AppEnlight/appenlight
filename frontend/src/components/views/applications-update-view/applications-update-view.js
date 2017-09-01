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

angular.module('appenlight.components.applicationsUpdateView', [])
    .component('applicationsUpdateView', {
        templateUrl: 'components/views/applications-update-view/applications-update-view.html',
        controller: applicationsUpdateViewController
    });

applicationsUpdateViewController.$inject = ['$state', 'applicationsNoIdResource', 'applicationsResource', 'applicationsPropertyResource', 'stateHolder', 'AeConfig'];

function applicationsUpdateViewController($state, applicationsNoIdResource, applicationsResource, applicationsPropertyResource, stateHolder, AeConfig) {
    'use strict';
    console.debug('applicationsUpdateView');
    var vm = this;
    vm.AeConfig = AeConfig;
    vm.$state = $state;
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
