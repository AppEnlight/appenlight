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


ApplicationsIntegrationsEditViewController.$inject = ['$state', 'integrationResource'];

function ApplicationsIntegrationsEditViewController($state, integrationResource) {
    console.debug('IntegrationController');
    var vm = this;
    vm.$onInit = function () {
        vm.$state = $state;
        vm.loading = {integration: true};
        vm.config = integrationResource.get(
            {
                integration: $state.params.integration,
                action: 'setup',
                resourceId: $state.params.resourceId
            }, function (data) {
                vm.loading.integration = false;
            });
    }
    vm.configureIntegration = function () {
        console.info('configureIntegration');
        vm.loading.integration = true;
        integrationResource.save(
            {
                integration: $state.params.integration,
                action: 'setup',
                resourceId: $state.params.resourceId
            }, vm.config, function (data) {
                vm.loading.integration = false;
                setServerValidation(vm.integrationForm);
            }, function (response) {
                if (response.status == 422) {
                    setServerValidation(vm.integrationForm, response.data);
                }
                vm.loading.integration = false;
            });
    };

    vm.removeIntegration = function () {
        console.info('removeIntegration');
        integrationResource.remove({
                integration: $state.params.integration,
                resourceId: $state.params.resourceId,
                action: 'delete'
            },
            function () {
                $state.go('applications.integrations',
                    {resourceId: $state.params.resourceId});
            }
        );
    }

    vm.testIntegration = function (to_test) {
        console.info('testIntegration', to_test);
        vm.loading.integration = true;
        integrationResource.save(
            {
                integration: $state.params.integration,
                action: 'test_' + to_test,
                resourceId: $state.params.resourceId
            }, vm.config, function (data) {
                vm.loading.integration = false;
            }, function (response) {
                vm.loading.integration = false;
            });
    }

    console.log(vm);
}
