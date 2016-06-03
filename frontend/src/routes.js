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

angular.module('appenlight').config(['$stateProvider', '$urlRouterProvider', function ($stateProvider, $urlRouterProvider) {

    $urlRouterProvider.otherwise('/ui');

    $stateProvider.state('logs', {
        url: '/ui/logs?resource',
        templateUrl: 'templates/logs.html',
        controller: 'LogsController as logs'
    });

    $stateProvider.state('front_dashboard', {
        url: '/ui',
        templateUrl: 'templates/dashboard.html',
        controller: 'IndexDashboardController as index'
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
        templateUrl: 'templates/events.html',
        controller: 'EventsController as events'
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
        url: '',
        templateUrl: 'templates/admin/configs/edit.html',
        controller: 'ConfigsListController as configs'
    });

    $stateProvider.state('user', {
        url: '/ui/user',
        templateUrl: 'templates/user/parent_view.html'
    });

    $stateProvider.state('user.profile', {
        abstract: true,
        url: '/profile',
        templateUrl: 'templates/user/profile.html'
    });
    $stateProvider.state('user.profile.edit', {
        url: '',
        templateUrl: 'templates/user/profile_edit.html',
        controller: 'UserProfileController as profile'
    });


    $stateProvider.state('user.profile.password', {
        url: '/password',
        templateUrl: 'templates/user/profile_password.html',
        controller: 'UserPasswordController as password'
    });

    $stateProvider.state('user.profile.identities', {
        url: '/identities',
        templateUrl: 'templates/user/profile_identities.html',
        controller: 'UserIdentitiesController as identities'
    });

    $stateProvider.state('user.profile.auth_tokens', {
        url: '/auth_tokens',
        templateUrl: 'templates/user/auth_tokens.html',
        controller: 'UserAuthTokensController as auth_tokens'
    });

    $stateProvider.state('user.alert_channels', {
        abstract: true,
        url: '/alert_channels',
        templateUrl: 'templates/user/alert_channels.html'
    });

    $stateProvider.state('user.alert_channels.list', {
        url: '',
        templateUrl: 'templates/user/alert_channels_list.html',
        controller: 'AlertChannelsController as channels'
    });

    $stateProvider.state('user.alert_channels.email', {
        url: '/email',
        templateUrl: 'templates/user/alert_channels_email.html',
        controller: 'AlertChannelsEmailController as email'
    });

    $stateProvider.state('applications', {
        abstract: true,
        url: '/ui/applications',
        templateUrl: 'templates/applications/parent_view.html'
    });

    $stateProvider.state('applications.list', {
        url: '',
        templateUrl: 'templates/applications/list.html',
        controller: 'ApplicationsListController as applications'
    });
    $stateProvider.state('applications.update', {
        url: '/{resourceId}/update',
        templateUrl: 'templates/applications/applications_update.html',
        controller: 'ApplicationsUpdateController as application'
    });

    $stateProvider.state('applications.integrations', {
        url: '/{resourceId}/integrations',
        templateUrl: 'templates/applications/integrations.html',
        controller: 'IntegrationsListController as integrations',
        data: {
            resource: null
        }
    });

    $stateProvider.state('applications.purge_logs', {
        url: '/purge_logs',
        templateUrl: 'templates/applications/applications_purge_logs.html',
        controller: 'ApplicationsPurgeLogsController as applications_purge'
    });

    $stateProvider.state('applications.integrations.edit', {
        url: '/{integration}',
        templateUrl: function ($stateParams) {
            return 'templates/applications/integrations/' + $stateParams.integration + '.html'
        },
        controller: 'IntegrationController as integration'
    });

    $stateProvider.state('tests', {
        url: '/ui/tests',
        templateUrl: 'templates/user/alert_channels_test.html',
        controller: 'AlertChannelsTestController as test_action'
    });

}]);
