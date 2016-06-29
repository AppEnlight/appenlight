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
