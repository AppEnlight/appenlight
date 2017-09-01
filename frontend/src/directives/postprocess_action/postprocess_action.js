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

angular.module('appenlight.directives.postProcessAction', []).directive('postProcessAction', ['applicationsPropertyResource', function (applicationsPropertyResource) {
    return {
        scope: {},
        bindToController:{
            action: '=',
            resource: '='
        },
        controller:postProcessActionController,
        controllerAs:'ctrl',
        restrict: 'E',
        templateUrl: 'directives/postprocess_action/postprocess_action.html'
    };
    function postProcessActionController(){
        var vm = this;
        console.log(vm);
        var allOps = {
            'eq': 'Equal',
            'ne': 'Not equal',
            'ge': 'Greater or equal',
            'gt': 'Greater than',
            'le': 'Lesser or equal',
            'lt': 'Lesser than',
            'startswith': 'Starts with',
            'endswith': 'Ends with',
            'contains': 'Contains'
        };

        var fieldOps = {};
        fieldOps['http_status'] = ['eq', 'ne', 'ge', 'le'];
        fieldOps['group:priority'] = ['eq', 'ne', 'ge', 'le'];
        fieldOps['duration'] = ['ge', 'le'];
        fieldOps['url_domain'] = ['eq', 'ne', 'startswith', 'endswith',
            'contains'];
        fieldOps['url_path'] = ['eq', 'ne', 'startswith', 'endswith',
            'contains'];
        fieldOps['error'] = ['eq', 'ne', 'startswith', 'endswith',
            'contains'];
        fieldOps['tags:server_name'] = ['eq', 'ne', 'startswith', 'endswith',
            'contains'];
        fieldOps['group:occurences'] = ['eq', 'ne', 'ge', 'le'];

        var possibleFields = {
            '__AND__': 'All met (composite rule)',
            '__OR__': 'One met (composite rule)',
            '__NOT__': 'Not met (composite rule)',
            'http_status': 'HTTP Status',
            'duration': 'Request duration',
            'group:priority': 'Group -> Priority',
            'url_domain': 'Domain',
            'url_path': 'URL Path',
            'error': 'Error',
            'tags:server_name': 'Tag -> Server name',
            'group:occurences': 'Group -> Occurences'
        };

        vm.ruleDefinitions = {
            fieldOps: fieldOps,
            allOps: allOps,
            possibleFields: possibleFields
        };

        vm.possibleActions = [
            ['1', 'Priority +1'],
            ['-1', 'Priority -1']
        ];

        vm.deleteAction = function (action) {
            applicationsPropertyResource.remove({
                pkey: vm.action.pkey,
                resourceId: vm.resource.resource_id,
                key: 'postprocessing_rules'
            }, function () {
                vm.resource.postprocessing_rules.splice(
                    vm.resource.postprocessing_rules.indexOf(action), 1);
            });
        };


        vm.saveAction = function () {
            var params = {
                'pkey': vm.action.pkey,
                'resourceId': vm.resource.resource_id,
                key: 'postprocessing_rules'
            };
            applicationsPropertyResource.update(params, vm.action,
                function (data) {
                    vm.action.dirty = false;
                    vm.errors = [];
                }, function (response) {
                    if (response.status == 422) {
                        var errorDict = angular.fromJson(response.data);
                        vm.errors = _.values(errorDict);
                    }
                });
        };

        vm.setDirty = function() {
            vm.action.dirty = true;
            console.log('set dirty');
        };
    }

}]);
