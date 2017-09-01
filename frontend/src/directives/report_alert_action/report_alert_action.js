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

angular.module('appenlight.directives.reportAlertAction', []).directive('reportAlertAction', ['userSelfPropertyResource', function (userSelfPropertyResource) {
    return {
        scope: {},
        bindToController:{
            action: '=',
            applications: '=',
            possibleChannels: '=',
            actions: '=',
            ruleDefinitions: '='
        },
        controller:reportAlertActionController,
        controllerAs:'ctrl',
        restrict: 'E',
        templateUrl: 'directives/report_alert_action/report_alert_action.html'
    };
    function reportAlertActionController(){
        var vm = this;
        vm.deleteAction = function (actions, action) {
            var get = {
                key: 'alert_channels_rules',
                pkey: action.pkey
            };
            userSelfPropertyResource.remove(get, function (data) {
                actions.splice(actions.indexOf(action), 1);
            });

        };

        vm.bindChannel = function(){
            var post = {
                channel_pkey: vm.channelToBind.pkey,
                action_pkey: vm.action.pkey
            };
            console.log(post);
            userSelfPropertyResource.save({key: 'alert_channels_actions_binds'}, post,
                function (data) {
                    vm.action.channels = [];
                    vm.action.channels = data.channels;
                }, function (response) {
                    if (response.status == 422) {
                        console.log('scope', response);
                    }
                });
        };

        vm.unBindChannel = function(channel){
            userSelfPropertyResource.delete({
                    key: 'alert_channels_actions_binds',
                    channel_pkey: channel.pkey,
                    action_pkey: vm.action.pkey
                },
                function (data) {
                    vm.action.channels = [];
                    vm.action.channels = data.channels;
                }, function (response) {
                    if (response.status == 422) {
                        console.log('scope', response);
                    }
                });
        };

        vm.saveAction = function () {
            var params = {
                key: 'alert_channels_rules',
                pkey: vm.action.pkey
            };
            userSelfPropertyResource.update(params, vm.action,
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

        vm.possibleNotifications = [
            ['always', 'Always'],
            ['only_first', 'Only New'],
        ];

        vm.possibleChannels = _.filter(vm.possibleChannels, function(c){
                return c.supports_report_alerting }
        );

        if (vm.possibleChannels.length > 0){
            vm.channelToBind = vm.possibleChannels[0];
        }

        vm.setDirty = function() {
            vm.action.dirty = true;
            console.log('set dirty');
        };
    }

}]);
