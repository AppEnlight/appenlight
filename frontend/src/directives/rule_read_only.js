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
        templateUrl: 'templates/directives/rule_read_only.html',
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
