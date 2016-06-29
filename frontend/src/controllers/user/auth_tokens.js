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

angular.module('appenlight.controllers').controller('UserAuthTokensController', UserAuthTokensController);

UserAuthTokensController.$inject = ['$filter', 'userSelfPropertyResource', 'AeConfig'];

function UserAuthTokensController($filter, userSelfPropertyResource, AeConfig) {
    console.debug('UserAuthTokensController');
    var vm = this;
    vm.loading = {tokens: true};

    vm.expireOptions = AeConfig.timeOptions;

    vm.tokens = userSelfPropertyResource.query({key: 'auth_tokens'},
        function (data) {
            vm.loading.tokens = false;
        });

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
    }

    vm.removeToken = function (token) {
        userSelfPropertyResource.delete({key: 'auth_tokens',
            token:token.token},
            function () {
                var index = vm.tokens.indexOf(token);
                if (index !== -1) {
                    vm.tokens.splice(index, 1);
                }
            })
    }
}
