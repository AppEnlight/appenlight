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

angular.module('appenlight.components.appenlightHeader', [])
    .component('appenlightHeader', {
        templateUrl: 'components/appenlight-header/appenlight-header.html',
        controller: AppEnlightHeaderController
    });

ChannelstreamController.$inject = ['$state', 'stateHolder', 'AeConfig'];

function AppEnlightHeaderController($state, stateHolder, AeConfig) {
    var vm = this;

    vm.$onInit = function () {

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
    }

    vm.clickedEvent = function (event) {
        // exception reports
        if (_.contains([1, 2], event.event_type)) {
            $state.go('report.list', {resource: event.resource_id, start_date: event.start_date});
        }
        // slowness reports
        else if (_.contains([3, 4], event.event_type)) {
            $state.go('report.list_slow', {resource: event.resource_id, start_date: event.start_date});
        }
        // uptime reports
        else if (_.contains([7, 8], event.event_type)) {
            $state.go('uptime', {resource: event.resource_id, start_date: event.start_date});
        } else {
            console.log('other');
        }
    }
}
