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

angular.module('appenlight.directives.ruleReadOnly', []).directive('ruleReadOnly', ['userSelfPropertyResource', function (userSelfPropertyResource) {
    return {
        scope: {},
        bindToController:{
            parentObj: '=',
            rule: '=',
            ruleDefinitions: '=',
            parentRule: "=",
            config: "="
        },
        restrict: 'E',
        templateUrl: 'directives/rule_read_only/rule_read_only.html',
        controller:RuleController,
        controllerAs:'rule_ctrlr'
    }
    function RuleController(){
        var vm = this;
        vm.readOnlyPossibleFields = {};
        var labelPairs = _.pairs(vm.parentObj.config);
        _.each(labelPairs, function (entry) {
            vm.readOnlyPossibleFields[entry[0]] = entry[1].human_label;
        });
    }
}]);
