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
