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

angular.module('appenlight.components.logsBrowserView', [])
    .component('logsBrowserView', {
        templateUrl: 'components/views/logs-browser/logs-browser.html',
        controller: LogsBrowserController
    });

LogsBrowserController.$inject = ['$location', 'stateHolder', 'typeAheadTagHelper', 'logsNoIdResource', 'sectionViewResource'];

function LogsBrowserController($location, stateHolder, typeAheadTagHelper, logsNoIdResource, sectionViewResource) {
    var vm = this;
    vm.$onInit = function () {
        vm.logEventsChartConfig = {
            data: {
                json: [],
                xFormat: '%Y-%m-%dT%H:%M:%S'
            },
            color: {
                pattern: ['#6baed6', '#e6550d', '#74c476', '#fdd0a2', '#8c564b']
            },
            axis: {
                x: {
                    type: 'timeseries',
                    tick: {
                        format: '%Y-%m-%d'
                    }
                },
                y: {
                    tick: {
                        count: 5,
                        format: d3.format('.2s')
                    }
                }
            },
            subchart: {
                show: true,
                size: {
                    height: 20
                }
            },
            size: {
                height: 250
            },
            zoom: {
                rescale: true
            },
            grid: {
                x: {
                    show: true
                },
                y: {
                    show: true
                }
            },
            tooltip: {
                format: {
                    title: function (d) {
                        return '' + d;
                    },
                    value: function (v) {
                        return v
                    }
                }
            }
        };
        vm.logEventsChartData = {};
        stateHolder.section = 'logs';
        vm.today = function () {
            vm.pickerDate = new Date();
        };
        vm.today();

        vm.applications = stateHolder.AeUser.applications_map;
        vm.logsPage = [];
        vm.itemCount = 0;
        vm.itemsPerPage = 250;
        vm.page = 1;
        vm.$location = $location;
        vm.isLoading = {
            logs: true,
            series: true
        };
        vm.filterTypeAheadOptions = [
            {
                type: 'message',
                text: 'message:',
                'description': 'Full-text search in your logs',
                tag: 'Message',
                example: 'message:text-im-looking-for'
            },
            {
                type: 'namespace',
                text: 'namespace:',
                'description': 'Query logs from specific namespace',
                tag: 'Namespace',
                example: "namespace:module.foo"
            },
            {
                type: 'resource',
                text: 'resource:',
                'description': 'Restrict resultset to application',
                tag: 'Application',
                example: "resource:ID"
            },
            {
                type: 'request_id',
                text: 'request_id:',
                'description': 'Show logs with specific request id',
                example: "request_id:883143dc572e4c38aceae92af0ea5ae0",
                tag: 'Request ID'
            },
            {
                type: 'level',
                text: 'level:',
                'description': 'Show entries with specific log level',
                example: 'level:warning',
                tag: 'Level'
            },
            {
                type: 'server_name',
                text: 'server_name:',
                'description': 'Show entries tagged with this key/value pair',
                example: 'server_name:hostname',
                tag: 'Tag'
            },
            {
                type: 'start_date',
                text: 'start_date:',
                'description': 'Show results newer than this date (press TAB for dropdown)',
                example: 'start_date:2014-08-15T13:00',
                tag: 'Start Date'
            },
            {
                type: 'end_date',
                text: 'end_date:',
                'description': 'Show results older than this date (press TAB for dropdown)',
                example: 'start_date:2014-08-15T23:59',
                tag: 'End Date'
            },
            {type: 'level', value: 'debug', text: 'level:debug'},
            {type: 'level', value: 'info', text: 'level:info'},
            {type: 'level', value: 'warning', text: 'level:warning'},
            {type: 'level', value: 'critical', text: 'level:critical'}
        ];
        vm.filterTypeAhead = null;
        vm.showDatePicker = false;
        vm.manualOpen = false;
        vm.aheadFilter = typeAheadTagHelper.aheadFilter;

        _.each(vm.applications, function (item) {
            vm.filterTypeAheadOptions.push({
                type: 'resource',
                text: 'resource:' + item.resource_id + ':' + item.resource_name,
                example: 'resource:' + item.resource_id,
                'tag': item.resource_name,
                'description': 'Restrict resultset to this application'
            });
        });
        console.info('page load');
        vm.refresh();
    }
    vm.removeSearchTag = function (tag) {
        $location.search(tag.type, null);
        vm.refresh();
    };
    vm.addSearchTag = function (tag) {
        $location.search(tag.type, tag.value);
        vm.refresh();
    };

    vm.paginationChange = function(){
        $location.search('page', vm.page);
        vm.refresh();
    };

    vm.typeAheadTag = function (event) {
        var text = vm.filterTypeAhead;
        if (_.isObject(vm.filterTypeAhead)) {
            text = vm.filterTypeAhead.text;
        };
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
            tag.value = parsed.slice(1).join(':');
        }
        else {
            tag.type = 'message';
            tag.value = parsed.join(':');
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
        vm.addSearchTag({type: tag.type, value: tag.value});
        // clear typeahead
        vm.filterTypeAhead = undefined;
    };


    vm.pickerDateChanged = function(){
        if (vm.filterTypeAhead.indexOf('start_date:') == '0') {
            vm.filterTypeAhead = 'start_date:' + moment(vm.pickerDate).utc().format();
        }
        else if (vm.filterTypeAhead.indexOf('end_date:') == '0') {
            vm.filterTypeAhead = 'end_date:' + moment(vm.pickerDate).utc().hour(23).minute(59).format();
        }
        vm.showDatePicker = false;
    };

    vm.fetchLogs = function (searchParams) {
        vm.isLoading.logs = true;
        logsNoIdResource.query(searchParams, function (data, getResponseHeaders) {
            vm.isLoading.logs = false;
            var headers = getResponseHeaders();
            vm.logsPage = data;
            vm.itemCount = headers['x-total-count'];
            vm.itemsPerPage = headers['x-items-per-page'];
        }, function () {
            vm.isLoading.logs = false;
        });
    };

    vm.fetchSeriesData = function (searchParams) {
        searchParams['section'] = 'logs_section';
        searchParams['view'] = 'fetch_series';
        vm.isLoading.series = true;
        sectionViewResource.query(searchParams, function (data) {
            console.log('show node here');
            vm.logEventsChartData = {
                json: data,
                xFormat: '%Y-%m-%dT%H:%M:%S',
                keys: {
                    x: 'x',
                    value: ["logs"]
                },
                names: {
                    logs: 'Log events'
                },
                type: 'bar'
            };
            vm.isLoading.series = false;
        }, function () {
            vm.isLoading.series = false;
        });
    };

    vm.filterId = function (log) {
        $location.search('request_id', log.request_id);
        vm.refresh();
    };

    vm.refresh = function(){
        vm.searchParams = parseSearchToTags($location.search());
        vm.page = Number(vm.searchParams.page) || 1;
        var params = parseTagsToSearch(vm.searchParams);
        vm.fetchLogs(params);
        vm.fetchSeriesData(params);
    };

}
