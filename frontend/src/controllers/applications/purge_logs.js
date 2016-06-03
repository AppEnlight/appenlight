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

angular.module('appenlight.controllers')
    .controller('ApplicationsPurgeLogsController', ApplicationsPurgeLogsController)

ApplicationsPurgeLogsController.$inject = ['applicationsResource', 'sectionViewResource', 'logsNoIdResource'];

function ApplicationsPurgeLogsController(applicationsResource, sectionViewResource, logsNoIdResource) {
    console.debug('ApplicationsPurgeLogsController');
    var vm = this;
    vm.loading = {applications: true};

    vm.namespace = null;
    vm.selectedResource = null;
    vm.commonNamespaces = [];

    vm.applications = applicationsResource.query({'type':'update_reports'}, function () {
        vm.loading.applications = false;
        vm.selectedResource = vm.applications[0].resource_id;
        vm.getCommonKeys();
    });

    /**
     * Fetches most commonly used tags in logs
     */
    vm.getCommonKeys = function () {
        sectionViewResource.get({
            section: 'logs_section',
            view: 'common_tags',
            resource: vm.selectedResource
        }, function (data) {
            vm.commonNamespaces = data['namespaces']
        });
    };

    vm.purgeLogs = function () {
        vm.loading.applications = true;
        logsNoIdResource.delete({resource:vm.selectedResource,
            namespace: vm.namespace}, function(){
            vm.loading.applications = false;
        });
    }
}
