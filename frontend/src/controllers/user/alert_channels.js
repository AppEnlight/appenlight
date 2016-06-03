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
// # App Enlight Enterprise Edition, including its added features, Support
// # services, and proprietary license terms, please see
// # https://rhodecode.com/licenses/

angular.module('appenlight.controllers').controller('AlertChannelsController', AlertChannelsController);

AlertChannelsController.$inject = ['userSelfPropertyResource', 'applicationsNoIdResource'];

function AlertChannelsController(userSelfPropertyResource, applicationsNoIdResource) {
    console.debug('AlertChannelsController');
    var vm = this;
    vm.loading = {channels: true, applications: true, actions:true};

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
            vm.alertChannels = _.filter(vm.alertChannels, function(item){
                return item != channel;
            });
        });

    }

}
