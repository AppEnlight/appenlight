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
        templateUrl: 'templates/directives/rule.html',
        controller:RuleController,
        controllerAs:'rule_ctrlr'
    };
    function RuleController(){
        var vm = this;

        vm.rule.dirty = false;
        vm.oldField = vm.rule.field;

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
