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

angular.module('appenlight.components.userAlertChannelsListView', [])
    .component('userAlertChannelsListView', {
        templateUrl: 'components/views/user-alert-channels-list-view/user-alert-channels-list-view.html',
        controller: userAlertChannelsListViewController
    });

userAlertChannelsListViewController.$inject = ['$state', 'userSelfPropertyResource', 'applicationsNoIdResource'];

function userAlertChannelsListViewController($state, userSelfPropertyResource, applicationsNoIdResource) {
    console.debug('AlertChannelsController');
    var vm = this;
    vm.$onInit = function () {
        vm.$state = $state;
        vm.loading = {channels: true, applications: true, actions: true};

        vm.alertChannels = userSelfPropertyResource.query({key: 'alert_channels'},
            function (data) {
                vm.loading.channels = false;
            });

        vm.alertActions = userSelfPropertyResource.query({key: 'alert_actions'},
            function (data) {
                vm.loading.actions = false;
            });

        vm.applications = applicationsNoIdResource.query({permission: 'view'},
            function (data) {
                vm.loading.applications = false;
            });

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
    }
    vm.addAction = function (channel) {
        console.log('test');
        userSelfPropertyResource.save({key: 'alert_channels_rules'}, {}, function (data) {
            vm.alertActions.push(data);
        }, function (response) {
            if (response.status == 422) {
                console.log('scope', response);
            }
        });
    };

    vm.updateChannel = function (channel, subKey) {
        var params = {
            key: 'alert_channels',
            channel_name: channel['channel_name'],
            channel_value: channel['channel_value']
        };
        var toUpdate = {};
        if (['daily_digest', 'send_alerts'].indexOf(subKey) !== -1) {
            toUpdate[subKey] = !channel[subKey];
        }
        userSelfPropertyResource.update(params, toUpdate, function (data) {
            _.extend(channel, data);
        });
    };

    vm.removeChannel = function (channel) {
        console.log(channel);
        userSelfPropertyResource.delete({
            key: 'alert_channels',
            channel_name: channel.channel_name,
            channel_value: channel.channel_value
        }, function () {
            vm.alertChannels = _.filter(vm.alertChannels, function (item) {
                return item != channel;
            });
        });

    }

}
