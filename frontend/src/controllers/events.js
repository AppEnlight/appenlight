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

angular.module('appenlight.controllers').controller('EventsController', EventsController);

EventsController.$inject = ['eventsNoIdResource', 'eventsResource'];

function EventsController(eventsNoIdResource, eventsResource) {
    console.info('EventsController');
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
