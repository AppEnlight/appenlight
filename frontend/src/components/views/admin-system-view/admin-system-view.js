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

angular.module('appenlight.components.adminSystemView', [])
    .component('adminSystemView', {
        templateUrl: 'components/views/admin-system-view/admin-system-view.html',
        controller: AdminSystemViewController
    });

AdminSystemViewController.$inject = ['sectionViewResource'];

function AdminSystemViewController(sectionViewResource) {
    var vm = this;
    vm.tables = [];
    vm.loading = {system: true};
    sectionViewResource.get({
        section: 'admin_section',
        view: 'system'
    }, null, function (data) {
        vm.DBtables = data.db_tables;
        vm.ESIndices = data.es_indices;
        vm.queueStats = data.queue_stats;
        vm.systemLoad = data.system_load;
        vm.packages = data.packages;
        vm.processInfo = data.process_info;
        vm.disks = data.disks;
        vm.memory = data.memory;
        vm.selfInfo = data.self_info;

        vm.loading.system = false;
    });
};
