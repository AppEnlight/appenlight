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
