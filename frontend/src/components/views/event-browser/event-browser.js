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

angular.module('appenlight.components.eventBrowserView', [])
    .component('eventBrowserView', {
        templateUrl: 'components/views/event-browser/event-browser.html',
        controller: EventBrowserController
    });

EventBrowserController.$inject = ['eventsNoIdResource', 'eventsResource'];

function EventBrowserController(eventsNoIdResource, eventsResource) {
    console.info('EventBrowserController');
    var vm = this;

    vm.loading = {events: true};

    vm.events = eventsNoIdResource.query(
        {key: 'events'},
        function (data) {
            vm.loading.events = false;
        });


    vm.closeEvent = function (event) {
        console.log('closeEvent');
        eventsResource.update({eventId: event.id}, {status: 0}, function (data) {
            event.status = 0;
        });
    }

}
