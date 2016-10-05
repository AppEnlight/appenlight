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

'use strict';

// Declare app level module which depends on filters, and services
angular.module('appenlight.base', [
    'ngRoute',
    'ui.router',
    'ui.router.router',
    'underscore',
    'ui.bootstrap',
    'ngResource',
    'ngAnimate',
    'ngCookies',
    'smart-table',
    'angular-toArrayFilter',
    'mentio'
]);

angular.module('appenlight.filters', []);
angular.module('appenlight.templates', []);
angular.module('appenlight.controllers', [
    'appenlight.base'
]);
angular.module('appenlight.components', [
    'appenlight.components.channelstream',
    'appenlight.components.appenlightApp',
    'appenlight.components.appenlightHeader'
]);
angular.module('appenlight.directives', [
    'appenlight.directives.c3chart',
    'appenlight.directives.confirmValidate',
    'appenlight.directives.focus',
    'appenlight.directives.formErrors',
    'appenlight.directives.humanFormat',
    'appenlight.directives.isoToRelativeTime',
    'appenlight.directives.permissionsForm',
    'appenlight.directives.smallReportGroupList',
    'appenlight.directives.smallReportList',
    'appenlight.directives.pluginConfig',
    'appenlight.directives.recursive',
    'appenlight.directives.reportAlertAction',
    'appenlight.directives.postProcessAction',
    'appenlight.directives.rule',
    'appenlight.directives.ruleReadOnly'
]);
angular.module('appenlight.services', [
    'appenlight.services.chartResultParser',
    'appenlight.services.resources',
    'appenlight.services.stateHolder',
    'appenlight.services.typeAheadTagHelper',
    'appenlight.services.UUIDProvider'
]).value('version', '0.1');


var pluginsToLoad = _.map(decodeEncodedJSON(window.AE.plugins),
    function(item){
        return item.config.angular_module
    });
console.log(pluginsToLoad);
angular.module('appenlight.plugins', pluginsToLoad);

var app = angular.module('appenlight', [
    'appenlight.base',
    'appenlight.config',
    'appenlight.templates',
    'appenlight.filters',
    'appenlight.services',
    'appenlight.directives',
    'appenlight.controllers',
    'appenlight.components',
    'appenlight.plugins'
]);

// needs manual execution because of plugin files
function kickstartAE(initialUserData) {
    app.config(['$httpProvider', '$uibTooltipProvider', '$locationProvider', function ($httpProvider, $uibTooltipProvider, $locationProvider) {
        $locationProvider.html5Mode(true);
        $httpProvider.interceptors.push(['$q', '$rootScope', '$timeout', 'stateHolder', function ($q, $rootScope, $timeout, stateHolder) {
            return {
                'response': function (response) {
                    var flashMessages = angular.fromJson(response.headers('x-flash-messages'));
                    if (flashMessages && flashMessages.length > 0) {
                        stateHolder.flashMessages.extend(flashMessages);
                    }
                    return response;
                },
                'responseError': function (rejection) {
                    if (rejection.status > 299 && rejection.status !== 422) {
                        stateHolder.flashMessages.extend([{
                            msg: 'Response status code: ' + rejection.status + ', "' + rejection.statusText + '", url: ' + rejection.config.url,
                            type: 'error'
                        }]);
                    }
                    if (rejection.status == 0) {
                        stateHolder.flashMessages.extend([{
                            msg: 'Response timeout',
                            type: 'error'
                        }]);
                    }
                    var flashMessages = angular.fromJson(rejection.headers('x-flash-messages'));
                    if (flashMessages && flashMessages.length > 0) {
                        stateHolder.flashMessages.extend(flashMessages);
                    }

                    return $q.reject(rejection);
                }
            }
        }]);

        $uibTooltipProvider.options({appendToBody: true});

    }]);


    app.config(function ($provide) {
        $provide.decorator("$exceptionHandler", function ($delegate) {
            return function (exception, cause) {
                $delegate(exception, cause);
                if (typeof AppEnlight !== 'undefined') {
                    AppEnlight.grabError(exception);
                }
            };
        });
    });

    app.run(['$rootScope', '$timeout', 'stateHolder', '$state', '$location', '$transitions', '$window', 'AeConfig',
        function ($rootScope, $timeout, stateHolder, $state, $location, $transitions, $window, AeConfig) {
            if (initialUserData){
                stateHolder.AeUser.update(initialUserData);
            }
            $rootScope.$state = $state;
            $rootScope.stateHolder = stateHolder;
            $rootScope.flash = stateHolder.flashMessages.list;
            $rootScope.closeAlert = stateHolder.flashMessages.closeAlert;
            $rootScope.AeConfig = AeConfig;

            var transitionApp = function($transition$, $state) {
                // redirect user to /register unless its one of open views
                var isGuestState = [
                        'report.view_detail',
                        'report.view_group',
                        'dashboard.view'
                    ].indexOf($transition$.to().name) !== -1;

                var path = $window.location.pathname;
                // strip trailing slash
                if (path.substr(path.length - 1) === '/') {
                    path = path.substr(0, path.length - 1);
                }
                var isOpenView = false;
                var openViews = [
                    AeConfig.urls.otherRoutes.lostPassword,
                    AeConfig.urls.otherRoutes.lostPasswordGenerate
                ];
                console.log('$transitions.onBefore', path, $transition$.to().name, $state);
                _.each(openViews, function (url) {
                    var url = '/' + url.split('/').slice(3).join('/');
                    if (url === path) {
                        isOpenView = true;
                    }
                });
                if (stateHolder.AeUser.id === null && !isGuestState && !isOpenView) {
                    if (window.location.toString().indexOf(AeConfig.urls.otherRoutes.register) === -1) {
                        console.log('redirect to register');
                        var newLocation = AeConfig.urls.otherRoutes.register + '?came_from=' + encodeURIComponent(window.location);
                        // fix infinite digest here
                        $rootScope.$on('$locationChangeStart',
                            function(event, toState, toParams, fromState, fromParams, options){
                                event.preventDefault();
                                $window.location = newLocation;
                            });
                        $window.location = newLocation;
                        return false;
                    }
                    return false;
                }
                return true;
            };
            $transitions.onBefore({}, transitionApp);

        }]);
}
