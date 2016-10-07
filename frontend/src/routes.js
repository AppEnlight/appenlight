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
        templateUrl: 'templates/reports/parent_view.html'
    });

    $stateProvider.state('report.list', {
        url: '?start_date&min_duration&max_duration&{view_name:any}&{server_name:any}&resource',
        templateUrl: 'templates/reports/list.html',
        controller: 'ReportsListController as reports_list'
    });

    $stateProvider.state('report.list_slow', {
        url: '/list_slow?start_date&min_duration&max_duration&{view_name:any}&{server_name:any}&resource',
        templateUrl: 'templates/reports/list_slow.html',
        controller: 'ReportsListSlowController as reports_list'
    });

    $stateProvider.state('report.view_detail', {
        url: '/:groupId/:reportId',
        templateUrl: 'templates/reports/view.html',
        controller: 'ReportsViewController as report'
    });
    $stateProvider.state('report.view_group', {
        url: '/:groupId',
        templateUrl: 'templates/reports/view.html',
        controller: 'ReportsViewController as report'
    });
    $stateProvider.state('events', {
        url: '/ui/events',
        component: 'eventBrowserView'
    });
    $stateProvider.state('admin', {
        url: '/ui/admin',
        templateUrl: 'templates/admin/parent_view.html'
    });
    $stateProvider.state('admin.user', {
        abstract: true,
        url: '/user',
        templateUrl: 'templates/admin/users/parent_view.html'
    });
    $stateProvider.state('admin.user.list', {
        url: '/list',
        templateUrl: 'templates/admin/users/users_list.html',
        controller: 'AdminUsersController as users'
    });
    $stateProvider.state('admin.user.create', {
        url: '/create',
        templateUrl: 'templates/admin/users/users_create.html',
        controller: 'AdminUsersCreateController as user'
    });
    $stateProvider.state('admin.user.update', {
        url: '/{userId}/update',
        templateUrl: 'templates/admin/users/users_create.html',
        controller: 'AdminUsersCreateController as user'
    });


    $stateProvider.state('admin.group', {
        abstract: true,
        url: '/group',
        templateUrl: 'templates/admin/groups/parent_view.html'
    });
    $stateProvider.state('admin.group.list', {
        url: '/list',
        templateUrl: 'templates/admin/groups/groups_list.html',
        controller: 'AdminGroupsController as groups'
    });
    $stateProvider.state('admin.group.create', {
        url: '/create',
        templateUrl: 'templates/admin/groups/groups_create.html',
        controller: 'AdminGroupsCreateController as group'
    });
    $stateProvider.state('admin.group.update', {
        url: '/{groupId}/update',
        templateUrl: 'templates/admin/groups/groups_create.html',
        controller: 'AdminGroupsCreateController as group'
    });

    $stateProvider.state('admin.application', {
        abstract: true,
        url: '/application',
        templateUrl: 'templates/admin/users/parent_view.html'
    });

    $stateProvider.state('admin.application.list', {
        url: '/list',
        templateUrl: 'templates/admin/applications/applications_list.html',
        controller: 'AdminApplicationsListController as applications'
    });

    $stateProvider.state('admin.partitions', {
        url: '/partitions',
        templateUrl: 'templates/admin/partitions.html',
        controller: 'AdminPartitionsController as partitions'
    });
    $stateProvider.state('admin.system', {
        url: '/system',
        templateUrl: 'templates/admin/system.html',
        controller: 'AdminSystemController as system'
    });

    $stateProvider.state('admin.configs', {
        abstract: true,
        url: '/configs',
        templateUrl: 'templates/admin/configs/parent_view.html'
    });

    $stateProvider.state('admin.configs.list', {
        url: '/list',
        templateUrl: 'templates/admin/configs/edit.html',
        controller: 'ConfigsListController as configs'
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
