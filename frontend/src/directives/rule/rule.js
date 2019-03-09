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

angular.module('appenlight.directives.rule', []).directive('rule', function () {
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
        templateUrl: 'directives/rule/rule.html',
        controller:RuleController,
        controllerAs:'rule_ctrlr'
    };
    function RuleController(){
        var vm = this;
        vm.$onInit = function () {
            vm.rule.dirty = false;
            vm.oldField = vm.rule.field;
        }
        vm.add = function () {
            vm.rule.rules.push(
                {op: "eq", field: 'http_status', value: ""}
            );
            vm.setDirty();
        };

        vm.setDirty = function() {
            vm.rule.dirty = true;
            console.log('set dirty');
            if (vm.parentObj){
                console.log('p', vm.parentObj);
                console.log('set parent dirty');
                vm.parentObj.dirty = true;
            }
        };

        vm.fieldChange = function () {
            var compound_types = ['__AND__', '__OR__', '__NOT__'];
            var new_is_compound = compound_types.indexOf(vm.rule.field) !== -1;
            var old_was_compound = compound_types.indexOf(vm.oldField) !== -1;

            if (!new_is_compound) {
                vm.rule.op = vm.ruleDefinitions.fieldOps[vm.rule.field][0];
            }
            if ((new_is_compound && !old_was_compound)) {
                console.log('resetting config');
                delete vm.rule.value;
                vm.rule.rules = [];
                vm.add();
            }
            else if (!new_is_compound && old_was_compound) {
                console.log('resetting config');
                delete vm.rule.rules;
                vm.rule.value = '';
            }
            vm.oldField = vm.rule.field;
            vm.setDirty();
        };

        vm.deleteRule = function (parent, rule) {
            parent.rules.splice(parent.rules.indexOf(rule), 1);
            vm.setDirty();
        }
    }
});
