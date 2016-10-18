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

var aeconfig = angular.module('appenlight.config', []);
aeconfig.factory('AeConfig', function () {
    var obj = {};
    obj.flashMessages = decodeEncodedJSON(window.AE.flash_messages);
    obj.timeOptions = decodeEncodedJSON(window.AE.timeOptions);
    obj.plugins = decodeEncodedJSON(window.AE.plugins);
    obj.topNav = {
        menuDashboardsItems: [],
        menuReportsItems: [],
        menuLogsItems: [],
        menuSettingsItems: [],
        menuAdminItems: []
    };
    obj.settingsNav = {
        menuApplicationsItems: [],
        menuUserSettingsItems: [],
        menuNotificationsItems: []
    };
    obj.adminNav = {
        menuUsersItems: [],
        menuResourcesItems: [],
        menuSystemItems: []
    };
    obj.ws_url = window.AE.ws_url;
    obj.urls = window.AE.urls;
    // set keys on values because we wont be able to retrieve them everywhere
    for (var key in obj.timeOptions) {
        obj.timeOptions[key]['key'] = key;
    }
    console.info('config', obj);
    return obj;
});
