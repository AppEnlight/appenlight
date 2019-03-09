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

angular.module('appenlight.components.userIdentitiesView', [])
    .component('userIdentitiesView', {
        templateUrl: 'components/views/user-identities-view/user-identities-view.html',
        controller: UserIdentitiesController
    });

UserIdentitiesController.$inject = ['$state', 'userSelfPropertyResource', 'AeConfig'];

function UserIdentitiesController($state, userSelfPropertyResource, AeConfig) {
    console.debug('UserIdentitiesController');
    var vm = this;
    vm.$onInit = function () {
        vm.$state = $state;
        vm.AeConfig = AeConfig;
        vm.loading = {identities: true};

        vm.identities = userSelfPropertyResource.query(
            {key: 'external_identities'},
            function (data) {
                vm.loading.identities = false;
                console.log(vm.identities);
            });
    }
    vm.removeProvider = function (provider) {
        console.log('provider', provider);
        userSelfPropertyResource.delete(
            {
                key: 'external_identities',
                provider: provider.provider,
                id: provider.id
            },
            function (status) {
                if (status) {
                    vm.identities = _.filter(vm.identities, function (item) {
                        return item != provider
                    });
                }

            });
    }
}
