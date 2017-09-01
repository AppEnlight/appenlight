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

angular.module('appenlight.components.adminConfigurationView', [])
    .component('adminConfigurationView', {
        templateUrl: 'components/views/admin-configuration-view/admin-configuration-view.html',
        controller: AdminConfigurationViewController
    });

AdminConfigurationViewController.$inject = ['configsResource', 'configsNoIdResource'];

function AdminConfigurationViewController(configsResource, configsNoIdResource) {
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
