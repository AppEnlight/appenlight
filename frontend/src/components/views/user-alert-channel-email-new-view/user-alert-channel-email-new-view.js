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

angular.module('appenlight.components.userAlertChannelsEmailNewView', [])
    .component('userAlertChannelsEmailNewView', {
        templateUrl: 'components/views/user-alert-channel-email-new-view/user-alert-channel-email-new-view.html',
        controller: AlertChannelsEmailController
    });

AlertChannelsEmailController.$inject = ['$state','userSelfPropertyResource'];

function AlertChannelsEmailController($state, userSelfPropertyResource) {
    console.debug('AlertChannelsEmailController');
    var vm = this;
    vm.$state = $state;
    vm.loading = {email: false};
    vm.form = {};

    vm.createChannel = function () {
        vm.loading.email = true;
        console.log('createChannel');
        userSelfPropertyResource.save({key: 'alert_channels'}, vm.form, function () {
            //vm.loading.email = false;
            //setServerValidation(vm.channelForm);
            //vm.form = {};
            $state.go('user.alert_channels.list');
        }, function (response) {
            if (response.status == 422) {
                setServerValidation(vm.channelForm, response.data);
            }
            vm.loading.email = false;
        });
    }
}
