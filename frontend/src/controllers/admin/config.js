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

angular.module('appenlight.controllers').controller('ConfigsListController', ConfigsListController);

ConfigsListController.$inject = ['configsResource', 'configsNoIdResource'];

function ConfigsListController(configsResource, configsNoIdResource) {
    var vm = this;
    vm.loading = {config: true};

    var filters = [
        'template_footer_html:global',
        'list_groups_to_non_admins:global',
        'per_application_reports_rate_limit:global',
        'per_application_logs_rate_limit:global',
        'per_application_metrics_rate_limit:global',
    ];

    vm.configs = {};

    vm.configList = configsResource.query({filter: filters},
        function (data) {
            vm.loading = {config: false};
            _.each(data, function (item) {
                if (vm.configs[item.section] === undefined) {
                    vm.configs[item.section] = {};
                }
                vm.configs[item.section][item.key] = item;
            });
        });

    vm.save = function () {
        vm.loading.config = true;
        _.each(vm.configList, function (item) {
            item.$save();
        });
        vm.loading.config = false;
    };

};
