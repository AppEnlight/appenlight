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
    .controller('UserIdentitiesController', UserIdentitiesController)

UserIdentitiesController.$inject = ['userSelfPropertyResource'];

function UserIdentitiesController(userSelfPropertyResource) {
    console.debug('UserIdentitiesController');
    var vm = this;
    vm.loading = {identities: true};

    vm.identities = userSelfPropertyResource.query(
        {key: 'external_identities'},
        function (data) {
            vm.loading.identities = false;
            console.log(vm.identities);
        });

    vm.removeProvider = function (provider) {
        console.log('provider', provider);
        userSelfPropertyResource.delete(
            {
                key: 'external_identities',
                provider: provider.provider,
                id: provider.id
            },
            function (status) {
                if (status){
                    vm.identities = _.filter(vm.identities, function (item) {
                        return item != provider
                    });
                }

            });
    }
}
