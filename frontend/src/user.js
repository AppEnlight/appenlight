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

function buildUser(jsonData){
    var AeUser = {
        user_name: jsonData.user_name || null,
        id: jsonData.id,
        assigned_reports: jsonData.assigned_reports || null,
        latest_events: jsonData.latest_events || null,
        permissions: jsonData.permissions || null,
        groups: jsonData.groups || null,
        applications: [],
        dashboards: []
    };
    AeUser.applications_map = {};
    AeUser.dashboards_map = {};
    AeUser.addApplication = function (item) {
        AeUser.applications.push(item);
        AeUser.applications_map[item.resource_id] = item;
    };
    AeUser.addDashboard = function (item) {
        AeUser.dashboards.push(item);
        AeUser.dashboards_map[item.resource_id] = item;
    };

    AeUser.removeApplicationById = function (applicationId) {
        AeUser.applications = _.filter(AeUser.applications, function (item) {
            return item.resource_id != applicationId;
        });
        delete AeUser.applications_map[applicationId];
    };
    AeUser.removeDashboardById = function (dashboardId) {
        AeUser.dashboards = _.filter(AeUser.dashboards, function (item) {
            return item.resource_id != dashboardId;
        });
        delete AeUser.dashboards_map[dashboardId];
    };

    AeUser.hasAppPermission = function (perm_name) {
        if (AeUser.permissions.indexOf('root_administration') !== -1) {
            return true
        }
        return AeUser.permissions.indexOf(perm_name) !== -1;
    };

    AeUser.hasContextPermission = function (permName, ACLList) {
        var hasPerm = false;
        _.each(ACLList, function (ACL) {
            // is this the right perm?
            if (ACL.perm_name == permName ||
                ACL.perm_name == '__all_permissions__') {
                // perm for this user or a group user belongs to
                if (ACL.user_name === AeUser.user_name ||
                    AeUser.groups.indexOf(ACL.group_name) !== -1) {
                    hasPerm = true
                }
            }
        });
        console.log('AeUser.hasContextPermission', permName, hasPerm);
        return hasPerm;
    };

    _.each(jsonData.applications, function (item) {
        AeUser.addApplication(item);
    });
    _.each(jsonData.dashboards, function (item) {
        AeUser.addDashboard(item);
    });
    return AeUser;
}
