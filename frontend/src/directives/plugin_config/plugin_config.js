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

angular.module('appenlight.directives.pluginConfig', []).directive('pluginConfig', function () {
    return {
        scope: {},
        bindToController: {
            resource: '=',
            section: '='
        },
        restrict: 'E',
        templateUrl: 'directives/plugin_config/plugin_config.html',
        controller: PluginConfig,
        controllerAs: 'plugin_ctrlr'
    };

    PluginConfig.$inject = ['stateHolder'];

    function PluginConfig(stateHolder) {
        this.plugins = {};
        this.inclusions = stateHolder.plugins.inclusions[this.section];
    }
});
