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

angular.module('appenlight.components.appenlightApp', [])
    .component('appenlightApp', {
        templateUrl: 'components/appenlight-app/appenlight-app.html',
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
