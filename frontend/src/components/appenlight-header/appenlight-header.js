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

angular.module('appenlight.components.appenlightHeader', [])
    .component('appenlightHeader', {
        templateUrl: 'components/appenlight-header/appenlight-header.html',
        controller: AppEnlightHeaderController
    });

ChannelstreamController.$inject = ['$state', 'stateHolder', 'AeConfig'];

function AppEnlightHeaderController($state, stateHolder, AeConfig){
    var vm = this;
    vm.AeConfig = AeConfig;
    vm.stateHolder = stateHolder;
    vm.assignedReports = stateHolder.AeUser.assigned_reports;
    vm.latestEvents = stateHolder.AeUser.latest_events;
    vm.activeEvents = 0;
    _.each(vm.latestEvents, function (event) {
        if (event.status === 1 && event.end_date === null) {
            vm.activeEvents += 1;
        }
    });

    vm.clickedEvent = function(event){
        // exception reports
        if (_.contains([1,2], event.event_type)){
            $state.go('report.list', {resource:event.resource_id, start_date:event.start_date});
        }
        // slowness reports
        else if (_.contains([3,4], event.event_type)){
            $state.go('report.list_slow', {resource:event.resource_id, start_date:event.start_date});
        }
        // uptime reports
        else if (_.contains([7,8], event.event_type)){
            $state.go('uptime', {resource:event.resource_id, start_date:event.start_date});
        }
        else{
            console.log('other');
        }
    }
}
