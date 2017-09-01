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

angular.module('appenlight').config(['$stateProvider', '$urlRouterProvider', function ($stateProvider, $urlRouterProvider) {

    $urlRouterProvider.otherwise('/ui');

    $stateProvider.state('logs', {
        url: '/ui/logs?resource',
        component: 'logsBrowserView'
    });

    $stateProvider.state('front_dashboard', {
        url: '/ui',
        component: 'indexDashboardView'
    });
    
    $stateProvider.state('report', {
        abstract: true,
        url: '/ui/report',
        template: '<ui-view></ui-view>'
    });

    $stateProvider.state('report.list', {
        url: '/list?start_date&min_duration&max_duration&{view_name:any}&{server_name:any}&resource',
        component: 'reportsBrowserView'
    });

    $stateProvider.state('report.list_slow', {
        url: '/list_slow?start_date&min_duration&max_duration&{view_name:any}&{server_name:any}&resource',
        component: 'reportsSlowBrowserView'
    });

    $stateProvider.state('report.view_detail', {
        url: '/:groupId/:reportId',
        component: 'reportView'
    });
    $stateProvider.state('report.view_group', {
        url: '/:groupId',
        component: 'reportView'
    });
    $stateProvider.state('events', {
        url: '/ui/events',
        component: 'eventBrowserView'
    });
    $stateProvider.state('admin', {
        url: '/ui/admin',
        component: 'adminView'
    });
    $stateProvider.state('admin.user', {
        abstract: true,
        url: '/user',
        template: '<ui-view></ui-view>'
    });
    $stateProvider.state('admin.user.list', {
        url: '/list',
        component: 'adminUsersListView'
    });
    $stateProvider.state('admin.user.create', {
        url: '/create',
        component: 'adminUsersCreateView'
    });
    $stateProvider.state('admin.user.update', {
        url: '/{userId}/update',
        component: 'adminUsersCreateView'
    });


    $stateProvider.state('admin.group', {
        abstract: true,
        url: '/group',
        template: '<ui-view></ui-view>'
    });
    $stateProvider.state('admin.group.list', {
        url: '/list',
        component: 'adminGroupsListView'
    });
    $stateProvider.state('admin.group.create', {
        url: '/create',
        component: 'adminGroupsCreateView'
    });
    $stateProvider.state('admin.group.update', {
        url: '/{groupId}/update',
        component: 'adminGroupsCreateView'
    });

    $stateProvider.state('admin.application', {
        abstract: true,
        url: '/application',
        template: '<ui-view></ui-view>'
    });

    $stateProvider.state('admin.application.list', {
        url: '/list',
        component: 'adminApplicationsListView'
    });

    $stateProvider.state('admin.partitions', {
        url: '/partitions',
        component: 'adminPartitionsView'
    });
    $stateProvider.state('admin.system', {
        url: '/system',
        component: 'adminSystemView'
    });

    $stateProvider.state('admin.configs', {
        abstract: true,
        url: '/configs',
        template: '<ui-view></ui-view>'
    });

    $stateProvider.state('admin.configs.list', {
        url: '/list',
        component: 'adminConfigurationView'
    });

    $stateProvider.state('user', {
        url: '/ui/user',
        component: 'settingsView'
    });

    $stateProvider.state('user.profile', {
        abstract: true,
        template: '<ui-view></ui-view>'
    });
    $stateProvider.state('user.profile.edit', {
        url: '/profile',
        component: 'userProfileView'
    });


    $stateProvider.state('user.profile.password', {
        url: '/password',
        component: 'userPasswordView'
    });

    $stateProvider.state('user.profile.identities', {
        url: '/identities',
        component: 'userIdentitiesView'
    });

    $stateProvider.state('user.profile.auth_tokens', {
        url: '/auth_tokens',
        component: 'userAuthTokensView'
    });

    $stateProvider.state('user.alert_channels', {
        abstract: true,
        url: '/alert_channels',
        template: '<ui-view></ui-view>'
    });

    $stateProvider.state('user.alert_channels.list', {
        url: '/list',
        component: 'userAlertChannelsListView'
    });

    $stateProvider.state('user.alert_channels.email', {
        url: '/email',
        component: 'userAlertChannelsEmailNewView'
    });

    $stateProvider.state('applications', {
        abstract: true,
        url: '/ui/applications',
        component: 'settingsView'
    });

    $stateProvider.state('applications.list', {
        url: '/list',
        component: 'applicationsListView'
    });
    $stateProvider.state('applications.update', {
        url: '/{resourceId}/update',
        component: 'applicationsUpdateView'
    });

    $stateProvider.state('applications.integrations', {
        url: '/{resourceId}/integrations',
        component: 'integrationsListView',
        data: {
            resource: null
        }
    });

    $stateProvider.state('applications.purge_logs', {
        url: '/purge_logs',
        component: 'applicationsPurgeLogsView'
    });

    $stateProvider.state('applications.integrations.edit', {
        url: '/{integration}',
        template: function ($stateParams) {
            return '<'+ $stateParams.integration + '-integration-config-view>'
        }
    });

    $stateProvider.state('tests', {
        url: '/ui/tests',
        templateUrl: 'templates/user/alert_channels_test.html',
        controller: 'AlertChannelsTestController as test_action'
    });

}]);
