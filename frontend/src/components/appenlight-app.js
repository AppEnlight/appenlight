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

angular.module('appenlight.components.appenlightApp', [])
    .component('appenlightApp', {
        templateUrl: 'templates/components/appenlight-app.html',
        controller: AppEnlightAppController
    });

AppEnlightAppController.$inject = ['$scope','$state', 'stateHolder', 'AeConfig'];

function AppEnlightAppController($scope, $state, stateHolder, AeConfig){
    console.log('app start');
    // to keep bw compatibility
    $scope.$state = $state;
    $scope.stateHolder = stateHolder;
    $scope.flash = stateHolder.flashMessages.list;
    $scope.closeAlert = stateHolder.flashMessages.closeAlert;
    $scope.AeConfig = AeConfig;
}
