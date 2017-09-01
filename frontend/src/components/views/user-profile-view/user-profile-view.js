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

angular.module('appenlight.components.userProfileView', [])
    .component('userProfileView', {
        templateUrl: 'components/views/user-profile-view/user-profile-view.html',
        controller: UserProfileViewController
    });

UserProfileViewController.$inject = ['$state', 'userSelfResource'];

function UserProfileViewController($state, userSelfResource) {
    console.debug('UserProfileViewController');
    var vm = this;
    vm.$state = $state;
    vm.loading = {profile: true};

    vm.user = userSelfResource.get(null, function (data) {
        vm.loading.profile = false;
        console.log('loaded profile');
    });

    vm.updateProfile = function () {
        vm.loading.profile = true;

        console.log('updateProfile');
        vm.user.$update(null, function () {
            vm.loading.profile = false;
            setServerValidation(vm.profileForm);
        }, function (response) {
            if (response.status == 422) {
                setServerValidation(vm.profileForm, response.data);
            }
            vm.loading.profile = false;
        });
    }
}
