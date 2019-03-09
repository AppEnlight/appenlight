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

angular.module('appenlight.components.userAuthTokensView', [])
    .component('userAuthTokensView', {
        templateUrl: 'components/views/user-auth-tokens-view/user-auth-tokens-view.html',
        controller: userAuthTokensViewController
    });

userAuthTokensViewController.$inject = ['$state', 'userSelfPropertyResource', 'AeConfig'];

function userAuthTokensViewController($state, userSelfPropertyResource, AeConfig) {
    console.debug('userAuthTokensViewController');
    var vm = this;
    vm.$onInit = function () {
        vm.$state = $state;
        vm.loading = {tokens: true};

        vm.expireOptions = AeConfig.timeOptions;

        vm.tokens = userSelfPropertyResource.query({key: 'auth_tokens'},
            function (data) {
                vm.loading.tokens = false;
            });
    }
    vm.addToken = function () {
        vm.loading.tokens = true;
        userSelfPropertyResource.save({key: 'auth_tokens'},
            vm.form,
            function (data) {
                vm.loading.tokens = false;
                setServerValidation(vm.TokenForm);
                vm.form = {};
                vm.tokens.push(data);
            }, function (response) {
                vm.loading.tokens = false;
                if (response.status == 422) {
                    setServerValidation(vm.TokenForm, response.data);
                }
            })
    };

    vm.removeToken = function (token) {
        userSelfPropertyResource.delete({
                key: 'auth_tokens',
                token: token.token
            },
            function () {
                var index = vm.tokens.indexOf(token);
                if (index !== -1) {
                    vm.tokens.splice(index, 1);
                }
            })
    }
}
