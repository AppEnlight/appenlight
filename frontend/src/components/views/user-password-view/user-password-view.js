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

angular.module('appenlight.components.userPasswordView', [])
    .component('userPasswordView', {
        templateUrl: 'components/views/user-password-view/user-password-view.html',
        controller: UserPasswordViewController
    });

UserPasswordViewController.$inject = ['$state', 'userSelfPropertyResource'];

function UserPasswordViewController($state, userSelfPropertyResource) {
    console.debug('UserPasswordViewController');
    var vm = this;
    vm.$state = $state;
    vm.loading = {password: false};
    vm.form = {};

    vm.updatePassword = function () {
        vm.loading.password = true;
        console.log('updatePassword');
        userSelfPropertyResource.update({key: 'password'}, vm.form, function () {
            vm.loading.password = false;
            vm.form = {};
            setServerValidation(vm.passwordForm);
        }, function (response) {
            if (response.status == 422) {
                console.log('vm', vm);
                setServerValidation(vm.passwordForm, response.data);
                console.log(response.data);
            }
            vm.loading.password = false;
        });
    }
}
