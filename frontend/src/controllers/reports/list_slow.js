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

'use strict';

/* Controllers */

angular.module('appenlight.controllers')
    .controller('ReportsListSlowController', ReportsListSlowController);

ReportsListSlowController.$inject = ['$scope', '$location', '$cookies',
    'stateHolder', 'typeAheadTagHelper', 'slowReportsResource', 'AeUser']

function ReportsListSlowController($scope, $location, $cookies, stateHolder, typeAheadTagHelper, slowReportsResource, AeUser) {
    var vm = this;
    vm.applications = AeUser.applications_map;
    stateHolder.section = 'slow_reports';
    vm.today = function () {
        vm.pickerDate = new Date();
    };
    vm.today();
    vm.reportsPage = [];
    vm.itemCount = 0;
    vm.itemsPerPage = 250;
    typeAheadTagHelper.tags = [];
    vm.searchParams = {tags: [], page: 1, type: 'slow_report'};
    vm.searchParams = parseSearchToTags($location.search());
    vm.is_loading = false;
    vm.filterTypeAheadOptions = [
        {
            type: 'view_name',
            text: 'view_name:',
            'description': 'Query reports occured in specific views',
            tag: 'View Name',
            example: "view_name:module.foo"
        },
        {
            type: 'resource',
            text: 'resource:',
            'description': 'Restrict resultset to application',
            tag: 'Application',
            example: "resource:ID"
        },
        {
            type: 'priority',
            text: 'priority:',
            'description': 'Show reports with specific priority',
            example: 'priority:8',
            tag: 'Priority'
        },
        {
            type: 'min_occurences',
            text: 'min_occurences:',
            'description': 'Show reports from groups with at least X occurences',
            example: 'min_occurences:25',
            tag: 'Min. occurences'
        },
        {
            type: 'min_duration',
            text: 'min_duration:',
            'description': 'Show reports from groups with average duration >= Xs',
            example: 'min_duration:4.5',
            tag: 'Min. duration'
        },
        {
            type: 'url_path',
            text: 'url_path:',
            'description': 'Show reports from specific URL paths',
            example: 'url_path:/foo/bar/baz',
            tag: 'Url Path'
        },
        {
            type: 'url_domain',
            text: 'url_domain:',
            'description': 'Show reports from specific domain',
            example: 'url_domain:domain.com',
            tag: 'Domain'
        },
        {
            type: 'request_id',
            text: 'request_id:',
            'description': 'Show reports with specific request id',
            example: "request_id:883143dc572e4c38aceae92af0ea5ae0",
            tag: 'Request ID'
        },
        {
            type: 'report_status',
            text: 'report_status:',
            'description': 'Show reports from groups with specific status',
            example: 'report_status:never_reviewed',
            tag: 'Status'
        },
        {
            type: 'server_name',
            text: 'server_name:',
            'description': 'Show reports tagged with this key/value pair',
            example: 'server_name:hostname',
            tag: 'Tag'
        },
        {
            type: 'start_date',
            text: 'start_date:',
            'description': 'Show reports newer than this date (press TAB for dropdown)',
            example: 'start_date:2014-08-15T13:00',
            tag: 'Start Date'
        },
        {
            type: 'end_date',
            text: 'end_date:',
            'description': 'Show reports older than this date (press TAB for dropdown)',
            example: 'start_date:2014-08-15T23:59',
            tag: 'End Date'
        }
    ];

    vm.filterTypeAhead = undefined;
    vm.showDatePicker = false;
    vm.aheadFilter = typeAheadTagHelper.aheadFilter;
    vm.removeSearchTag = function (tag) {
        $location.search(tag.type, null);
    };
    vm.addSearchTag = function (tag) {
        $location.search(tag.type, tag.value);
    };
    vm.manualOpen = false;
    vm.notRelativeTime = false;
    if ($cookies.notRelativeTime) {
        vm.notRelativeTime = JSON.parse($cookies.notRelativeTime);
    }


    vm.changeRelativeTime = function () {
        $cookies.notRelativeTime = JSON.stringify(vm.notRelativeTime);
    };

    _.each(_.range(1, 11), function (priority) {
        vm.filterTypeAheadOptions.push({
            type: 'priority',
            text: 'priority:' + priority.toString(),
            description: 'Show entries with specific priority',
            example: 'priority:' + priority,
            tag: 'Priority'
        });
    });
    _.each(['never_reviewed', 'reviewed', 'fixed', 'public'], function (status) {
        vm.filterTypeAheadOptions.push({
            type: 'report_status',
            text: 'report_status:' + status,
            'description': 'Show only reports with this status',
            example: 'report_status:' + status,
            tag: 'Status ' + status.toUpperCase()
        });
    });
    _.each(AeUser.applications, function (item) {
        vm.filterTypeAheadOptions.push({
            type: 'resource',
            text: 'resource:' + item.resource_id + ':' + item.resource_name,
            example: 'resource:' + item.resource_id,
            'tag': item.resource_name,
            'description': 'Restrict resultset to this application'
        });
    });

    vm.typeAheadTag = function (event) {
        var text = vm.filterTypeAhead;
        if (_.isObject(vm.filterTypeAhead)) {
            text = vm.filterTypeAhead.text;
        }
        ;
        if (!vm.filterTypeAhead) {
            return
        }
        var parsed = text.split(':');
        var tag = {'type': null, 'value': null};
        // app tags have : twice
        if (parsed.length > 2 && parsed[0] == 'resource') {
            tag.type = 'resource';
            tag.value = parsed[1];
        }
        // normal tag:value
        else if (parsed.length > 1) {
            tag.type = parsed[0];
            var tagValue = parsed.slice(1);
            if (tagValue) {
                tag.value = tagValue.join(':');
            }
        }

        // set datepicker hour based on type of field
        if ('start_date:' == text) {
            vm.showDatePicker = true;
            vm.filterTypeAhead = 'start_date:' + moment(vm.pickerDate).utc().format();
        }
        else if ('end_date:' == text) {
            vm.showDatePicker = true;
            vm.filterTypeAhead = 'end_date:' + moment(vm.pickerDate).utc().hour(23).minute(59).format();
        }

        if (event.keyCode != 13 || !tag.type || !tag.value) {
            return
        }
        vm.showDatePicker = false;
        // aka we selected one of main options
        $location.search(tag.type, tag.value);
        // clear typeahead
        vm.filterTypeAhead = undefined;
    }

    vm.paginationChange = function(){
        $location.search('page', vm.searchParams.page);
    }

    vm.pickerDateChanged = function(){
        if (vm.filterTypeAhead.indexOf('start_date:') == '0') {
            vm.filterTypeAhead = 'start_date:' + moment(vm.pickerDate).utc().format();
        }
        else if (vm.filterTypeAhead.indexOf('end_date:') == '0') {
            vm.filterTypeAhead = 'end_date:' + moment(vm.pickerDate).utc().hour(23).minute(59).format();
        }
        vm.showDatePicker = false;
    }

    var reportPresentation = function (report) {
        report.presentation = {};
        if (report.group.public) {
            report.presentation.className = 'public';
            report.presentation.tooltip = 'Public';
        }
        else if (report.group.fixed) {
            report.presentation.className = 'fixed';
            report.presentation.tooltip = 'Fixed';
        }
        else if (report.group.read) {
            report.presentation.className = 'reviewed';
            report.presentation.tooltip = 'Reviewed';
        }
        else {
            report.presentation.className = 'new';
            report.presentation.tooltip = 'New';
        }
        return report;
    }

    vm.fetchReports = function (searchParams) {
        vm.is_loading = true;
        slowReportsResource.query(searchParams, function (data, getResponseHeaders) {
            var headers = getResponseHeaders();
            console.log(headers);
            vm.is_loading = false;
            vm.reportsPage = _.map(data, function (item) {
                return reportPresentation(item);
            });
            vm.itemCount = headers['x-total-count'];
            vm.itemsPerPage = headers['x-items-per-page'];
        }, function () {
            vm.is_loading = false;
        });
    }

    vm.filterId = function (log) {
        vm.searchParams.tags.push({
            type: "request_id",
            value: log.request_id
        });
    }
    //initial load
    var params = parseTagsToSearch(vm.searchParams);
    vm.fetchReports(params);

    $scope.$on('$locationChangeSuccess', function () {
        console.log('$locationChangeSuccess ReportsListSlowController ');
        vm.searchParams = parseSearchToTags($location.search());
        var params = parseTagsToSearch(vm.searchParams);
        console.log($location.path());
        if (vm.is_loading === false) {
            console.log(params);
            vm.fetchReports(params);
        }
    });


}
