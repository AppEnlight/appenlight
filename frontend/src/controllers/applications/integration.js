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

angular.module('appenlight.controllers')
    .controller('IntegrationController', IntegrationController)

IntegrationController.$inject = ['$state', 'integrationResource'];

function IntegrationController($state, integrationResource) {
    console.debug('IntegrationController');
    var vm = this;
    vm.loading = {integration: true};
    vm.config = integrationResource.get(
        {
            integration: $state.params.integration,
            action: 'setup',
            resourceId: $state.params.resourceId
        }, function (data) {
            vm.loading.integration = false;
        });

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

    vm.testIntegration = function(to_test){
        console.info('testIntegration', to_test);
        vm.loading.integration = true;
        integrationResource.save(
            {
                integration: $state.params.integration,
                action: 'test_'+ to_test,
                resourceId: $state.params.resourceId
            }, vm.config, function (data) {
                vm.loading.integration = false;
            }, function (response) {
                vm.loading.integration = false;
            });
    }

    console.log(vm);
}
