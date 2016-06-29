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
        templateUrl: 'templates/directives/report_alert_action.html'
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
