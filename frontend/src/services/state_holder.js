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

angular.module('appenlight.services.stateHolder', []).factory('stateHolder',
    ['$timeout', 'AeConfig', function ($timeout, AeConfig) {

    var AeUser = {"user_name": null, "id": null};
    AeUser.update = function (jsonData) {
        jsonData = jsonData || {};
        this.applications_map = {};
        this.dashboards_map = {};
        this.user_name = jsonData.user_name || null;
        this.id = jsonData.id;
        this.assigned_reports = jsonData.assigned_reports || null;
        this.latest_events = jsonData.latest_events || null;
        this.permissions = jsonData.permissions || null;
        this.groups = jsonData.groups || null;
        this.applications = [];
        this.dashboards = [];
        _.each(jsonData.applications, function (item) {
            this.addApplication(item);
        }.bind(this));
        _.each(jsonData.dashboards, function (item) {
            this.addDashboard(item);
        }.bind(this));
    };
    AeUser.addApplication = function (item) {
        this.applications.push(item);
        this.applications_map[item.resource_id] = item;
    };
    AeUser.addDashboard = function (item) {
        this.dashboards.push(item);
        this.dashboards_map[item.resource_id] = item;
    };

    AeUser.removeApplicationById = function (applicationId) {
        this.applications = _.filter(this.applications, function (item) {
            return item.resource_id != applicationId;
        });
        delete this.applications_map[applicationId];
    };
    AeUser.removeDashboardById = function (dashboardId) {
        this.dashboards = _.filter(this.dashboards, function (item) {
            return item.resource_id != dashboardId;
        });
        delete this.dashboards_map[dashboardId];
    };

    AeUser.hasAppPermission = function (perm_name) {
        if (this.permissions.indexOf('root_administration') !== -1) {
            return true
        }
        return this.permissions.indexOf(perm_name) !== -1;
    };

    AeUser.hasContextPermission = function (permName, ACLList) {
        var hasPerm = false;
        _.each(ACLList, function (ACL) {
            // is this the right perm?
            if (ACL.perm_name == permName ||
                ACL.perm_name == '__all_permissions__') {
                // perm for this user or a group user belongs to
                if (ACL.user_name === this.user_name ||
                    this.groups.indexOf(ACL.group_name) !== -1) {
                    hasPerm = true
                }
            }
        }.bind(this));
        console.log('AeUser.hasContextPermission', permName, hasPerm);
        return hasPerm;
    };

    /**
     * Holds some common stuff like flash messages, but important part is
     * plugins property that is a registry that holds all information about
     * loaded plugins, its mutated via  .run() functions on inclusion
     * @type {{list: Array, timeout: null, extend: flashMessages.extend, pop: flashMessages.pop, cancelTimeout: flashMessages.cancelTimeout, removeMessages: flashMessages.removeMessages}}
     */
    var flashMessages = {
        list: [],
        timeout: null,
        extend: function (values) {
            console.log('pushing flash', this);
            if (this.list.length > 2) {
                this.list.splice(0, this.list.length - 2);
            }
            this.list.push.apply(this.list, values);
            this.cancelTimeout();
            this.removeMessages();
        },
        pop: function () {
            console.log('popping flash');
            this.list.pop();
        },
        cancelTimeout: function () {
            if (this.timeout) {
                $timeout.cancel(this.timeout);
            }
        },
        removeMessages: function () {
            var self = this;
            this.timeout = $timeout(function () {
                while (self.list.length > 0) {
                    self.list.pop();
                }
            }, 10000);
        }
    };
    flashMessages.closeAlert = angular.bind(flashMessages, function (index) {
        this.list.splice(index, 1);
        this.cancelTimeout();
    });
    /* add flash messages from template generated on non-xhr request level */
    try {
        if (AeConfig.flashMessages.length > 0) {
            flashMessages.list = AeConfig.flashMessages;
        }
    }
    catch (exc) {

    }

    var Plugins = {
        enabled: [],
        configs: {},
        inclusions: {},
        addInclusion: function (name, inclusion) {
            var self = this;
            if (self.inclusions.hasOwnProperty(name) === false) {
                self.inclusions[name] = [];
            }
            self.inclusions[name].push(inclusion);
        }
    };

    var stateHolder = {
        section: 'settings',
        resource: null,
        plugins: Plugins,
        flashMessages: flashMessages,
        AeUser: AeUser,
        AeConfig: AeConfig
    };
    return stateHolder;
}]);
