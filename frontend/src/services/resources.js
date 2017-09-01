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

var DEFAULT_ACTIONS = {
    'get': {method: 'GET', timeout: 60000 * 2},
    'save': {method: 'POST', timeout: 60000 * 2},
    'query': {method: 'GET', isArray: true, timeout: 60000 * 2},
    'remove': {method: 'DELETE', timeout: 30000},
    'update': {method: 'PATCH', timeout: 30000},
    'delete': {method: 'DELETE', timeout: 30000}
};

angular.module('appenlight.services.resources', []).factory('usersResource', ['$resource', 'AeConfig', function ($resource, AeConfig) {
    return $resource(AeConfig.urls.users, {userId: '@id'}, angular.copy(DEFAULT_ACTIONS));
}]);

angular.module('appenlight.services.resources').factory('userResource', ['$resource', 'AeConfig', function ($resource, AeConfig) {
    return $resource(AeConfig.urls.user, null, angular.copy(DEFAULT_ACTIONS));
}]);

angular.module('appenlight.services.resources').factory('usersPropertyResource', ['$resource', 'AeConfig', function ($resource, AeConfig) {
    return $resource(AeConfig.urls.usersProperty, null, angular.copy(DEFAULT_ACTIONS));
}]);

angular.module('appenlight.services.resources').factory('userSelfResource', ['$resource', 'AeConfig', function ($resource, AeConfig) {
    return $resource(AeConfig.urls.userSelf, null, angular.copy(DEFAULT_ACTIONS));
}]);

angular.module('appenlight.services.resources').factory('userSelfPropertyResource', ['$resource', 'AeConfig', function ($resource, AeConfig) {
    return $resource(AeConfig.urls.userSelfProperty, null, angular.copy(DEFAULT_ACTIONS));
}]);

angular.module('appenlight.services.resources').factory('logsNoIdResource', ['$resource', 'AeConfig', function ($resource, AeConfig) {
    return $resource(AeConfig.urls.logsNoId, null, angular.copy(DEFAULT_ACTIONS));
}]);

angular.module('appenlight.services.resources').factory('reportsResource', ['$resource', 'AeConfig', function ($resource, AeConfig) {
    return $resource(AeConfig.urls.reports, null, angular.copy(DEFAULT_ACTIONS));
}]);

angular.module('appenlight.services.resources').factory('slowReportsResource', ['$resource', 'AeConfig', function ($resource, AeConfig) {
    return $resource(AeConfig.urls.slowReports, null, angular.copy(DEFAULT_ACTIONS));
}]);

angular.module('appenlight.services.resources').factory('reportGroupResource', ['$resource', 'AeConfig', function ($resource, AeConfig) {
    return $resource(AeConfig.urls.reportGroup, null, angular.copy(DEFAULT_ACTIONS));
}]);

angular.module('appenlight.services.resources').factory('reportGroupPropertyResource', ['$resource', 'AeConfig', function ($resource, AeConfig) {
    return $resource(AeConfig.urls.reportGroupProperty, null, angular.copy(DEFAULT_ACTIONS));
}]);


angular.module('appenlight.services.resources').factory('reportResource', ['$resource', 'AeConfig', function ($resource, AeConfig) {
    return $resource(AeConfig.urls.reports, null, angular.copy(DEFAULT_ACTIONS));
}]);

angular.module('appenlight.services.resources').factory('analyticsResource', ['$resource', 'AeConfig', function ($resource, AeConfig) {
    return $resource(AeConfig.urls.analyticsAction, null, angular.copy(DEFAULT_ACTIONS));
}]);

angular.module('appenlight.services.resources').factory('reportsResource', ['$resource', 'AeConfig', function ($resource, AeConfig) {
    return $resource(AeConfig.urls.reports, null, angular.copy(DEFAULT_ACTIONS));
}]);

angular.module('appenlight.services.resources').factory('integrationResource', ['$resource', 'AeConfig', function ($resource, AeConfig) {
    return $resource(AeConfig.urls.integrationAction, null, angular.copy(DEFAULT_ACTIONS));
}]);


angular.module('appenlight.services.resources').factory('adminResource', ['$resource', 'AeConfig', function ($resource, AeConfig) {
    return $resource(AeConfig.urls.adminAction, null, angular.copy(DEFAULT_ACTIONS));
}]);

angular.module('appenlight.services.resources').factory('applicationsNoIdResource', ['$resource', 'AeConfig', function ($resource, AeConfig) {
    return $resource(AeConfig.urls.applicationsNoId, null, angular.copy(DEFAULT_ACTIONS));
}]);

angular.module('appenlight.services.resources').factory('applicationsPropertyResource', ['$resource', 'AeConfig', function ($resource, AeConfig) {
    return $resource(AeConfig.urls.applicationsProperty, null, angular.copy(DEFAULT_ACTIONS));
}]);
angular.module('appenlight.services.resources').factory('applicationsResource', ['$resource', 'AeConfig', function ($resource, AeConfig) {
    return $resource(AeConfig.urls.applications, null, angular.copy(DEFAULT_ACTIONS));
}]);

angular.module('appenlight.services.resources').factory('sectionViewResource', ['$resource', 'AeConfig', function ($resource, AeConfig) {
    return $resource(AeConfig.urls.sectionView, null, angular.copy(DEFAULT_ACTIONS));
}]);

angular.module('appenlight.services.resources').factory('groupsNoIdResource', ['$resource', 'AeConfig', function ($resource, AeConfig) {
    return $resource(AeConfig.urls.groupsNoId, null, angular.copy(DEFAULT_ACTIONS));
}]);


angular.module('appenlight.services.resources').factory('groupsResource', ['$resource', 'AeConfig', function ($resource, AeConfig) {
    return $resource(AeConfig.urls.groups, {userId: '@id'}, angular.copy(DEFAULT_ACTIONS));
}]);

angular.module('appenlight.services.resources').factory('groupsPropertyResource', ['$resource', 'AeConfig', function ($resource, AeConfig) {
    return $resource(AeConfig.urls.groupsProperty, null, angular.copy(DEFAULT_ACTIONS));
}]);


angular.module('appenlight.services.resources').factory('eventsNoIdResource', ['$resource', 'AeConfig', function ($resource, AeConfig) {
    return $resource(AeConfig.urls.eventsNoId, null, angular.copy(DEFAULT_ACTIONS));
}]);


angular.module('appenlight.services.resources').factory('eventsResource', ['$resource', 'AeConfig', function ($resource, AeConfig) {
    return $resource(AeConfig.urls.events, {userId: '@id'}, angular.copy(DEFAULT_ACTIONS));
}]);

angular.module('appenlight.services.resources').factory('eventsPropertyResource', ['$resource', 'AeConfig', function ($resource, AeConfig) {
    return $resource(AeConfig.urls.eventsProperty, null, angular.copy(DEFAULT_ACTIONS));
}]);

angular.module('appenlight.services.resources').factory('configsNoIdResource', ['$resource', 'AeConfig', function ($resource, AeConfig) {
    return $resource(AeConfig.urls.configsNoId, null, angular.copy(DEFAULT_ACTIONS));
}]);

angular.module('appenlight.services.resources').factory('configsResource', ['$resource', 'AeConfig', function ($resource, AeConfig) {
    return $resource(AeConfig.urls.configs, {
        key: '@key',
        section: '@section'
    }, angular.copy(DEFAULT_ACTIONS));
}]);

angular.module('appenlight.services.resources').factory('pluginConfigsResource', ['$resource', 'AeConfig', function ($resource, AeConfig) {
    return $resource(AeConfig.urls.pluginConfigs, {
        id: '@id',
        plugin_name: '@plugin_name'
    }, angular.copy(DEFAULT_ACTIONS));
}]);

angular.module('appenlight.services.resources').factory('resourcesPropertyResource', ['$resource', 'AeConfig', function ($resource, AeConfig) {
    return $resource(AeConfig.urls.resourceProperty, null, angular.copy(DEFAULT_ACTIONS));
}]);
