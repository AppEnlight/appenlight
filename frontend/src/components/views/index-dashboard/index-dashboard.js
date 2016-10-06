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

angular.module('appenlight.components.indexDashboardView', [])
    .component('indexDashboardView', {
        templateUrl: 'components/views/index-dashboard/index-dashboard.html',
        controller: IndexDashboardController
    });

IndexDashboardController.$inject = ['$rootScope', '$scope', '$location','$cookies', '$interval', 'stateHolder', 'applicationsPropertyResource', 'AeConfig'];

function IndexDashboardController($rootScope, $scope, $location, $cookies, $interval, stateHolder, applicationsPropertyResource, AeConfig) {
    var vm = this;
    stateHolder.section = 'dashboard';
    vm.timeOptions = {};
    var allowed = ['1h', '4h', '12h', '24h', '1w', '2w', '1M'];
    _.each(allowed, function (key) {
        if (allowed.indexOf(key) !== -1) {
            vm.timeOptions[key] = AeConfig.timeOptions[key];
        }
    });
    vm.stateHolder = stateHolder;
    vm.urls = AeConfig.urls;
    vm.applications = stateHolder.AeUser.applications_map;
    vm.show_dashboard = false;
    vm.resource = null;
    vm.graphType = {selected: null};
    vm.timeSpan = vm.timeOptions['1h'];
    vm.trendingReports = [];
    vm.exceptions = 0;
    vm.satisfyingRequests = 0;
    vm.toleratedRequests = 0;
    vm.frustratingRequests = 0;
    vm.uptimeStats = 0;
    vm.apdexStats = [];
    vm.seriesRequestsData = [];
    vm.seriesMetricsData = [];
    vm.seriesSlowData = [];
    vm.slowCalls = [];
    vm.slowURIS = [];

    vm.reportChartConfig = {
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
                    culling: {
                        max: 6 // the number of tick texts will be adjusted to less than this value
                    },
                    format: '%Y-%m-%d %H:%M'
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
    vm.reportChartData = {};

    vm.reportSlowChartConfig = {
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
                    culling: {
                        max: 6 // the number of tick texts will be adjusted to less than this value
                    },
                    format: '%Y-%m-%d %H:%M'
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
    vm.reportSlowChartData = {};

    vm.metricsChartConfig = {
        data: {
            json: [],
            xFormat: '%Y-%m-%dT%H:%M:%S',
            keys: {
                x: 'x',
                value: ["main", "sql", "nosql", "tmpl", "remote", "custom"]
            },
            names: {
                main: 'View/Application logic',
                sql: 'Relational database queries',
                nosql: 'NoSql datastore calls',
                tmpl: 'Template rendering',
                custom: 'Custom timed calls',
                remote: 'Requests to remote resources'
            },
            type: 'area',
            groups: [["main", "sql", "nosql", "remote", "custom", "tmpl"]],
            order: null
        },
        color: {
            pattern: ['#6baed6', '#c7e9c0', '#fd8d3c', '#d6616b', '#ffcc00', '#c6dbef']
        },
        axis: {
            x: {
                type: 'timeseries',
                tick: {
                    culling: {
                        max: 6 // the number of tick texts will be adjusted to less than this value
                    },
                    format: '%Y-%m-%d %H:%M'
                }
            },
            y: {
                tick: {
                    count: 5,
                    format: d3.format('.2f')
                }
            }
        },
        point: {
            show: false
        },
        subchart: {
            show: true,
            size: {
                height: 20
            }
        },
        size: {
            height: 350
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
    vm.metricsChartData = {};

    vm.responseChartConfig = {
        data: {
            json: [],
            xFormat: '%Y-%m-%dT%H:%M:%S'
        },
        color: {
            pattern: ['#d6616b', '#6baed6', '#fd8d3c']
        },
        axis: {
            x: {
                type: 'timeseries',
                tick: {
                    culling: {
                        max: 6 // the number of tick texts will be adjusted to less than this value
                    },
                    format: '%Y-%m-%d %H:%M'
                }
            },
            y: {
                tick: {
                    count: 5,
                    format: d3.format('.2f')
                }
            }
        },
        point: {
            show: false
        },
        subchart: {
            show: true,
            size: {
                height: 20
            }
        },
        size: {
            height: 350
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
    vm.responseChartData = {};

    vm.requestsChartConfig = {
        data: {
            json: [],
            xFormat: '%Y-%m-%dT%H:%M:%S'
        },
        color: {
            pattern: ['#d6616b', '#6baed6', '#fd8d3c']
        },
        axis: {
            x: {
                type: 'timeseries',
                tick: {
                    culling: {
                        max: 6 // the number of tick texts will be adjusted to less than this value
                    },
                    format: '%Y-%m-%d %H:%M'
                }
            },
            y: {
                tick: {
                    count: 5,
                    format: d3.format('.2f')
                }
            }
        },
        point: {
            show: false
        },
        subchart: {
            show: true,
            size: {
                height: 20
            }
        },
        size: {
            height: 350
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
    vm.requestsChartData = {};

    vm.loading = {
        'apdex': true,
        'reports': true,
        'graphs': true,
        'slowCalls': true,
        'slowURIS': true,
        'requestsBreakdown': true,
        'series': true
    };
    vm.stream = {paused: false, filtered: false, messages: [], reports: []};

    $rootScope.$on('channelstream-message.front_dashboard.new_topic', function(event, message){
        var ws_report = message.message.report;
        if (ws_report.http_status != 500) {
            return
        }
        if (vm.stream.paused == true) {
            return
        }
        if (vm.stream.filtered && ws_report.resource_id != vm.resource) {
            return
        }
        var should_insert = true;
        _.each(vm.stream.reports, function (report) {
            if (report.report_id == ws_report.report_id) {
                report.occurences = ws_report.occurences;
                should_insert = false;
            }
        });
        if (should_insert) {
            if (vm.stream.reports.length > 7) {
                vm.stream.reports.pop();
            }
            vm.stream.reports.unshift(ws_report);
        }
    });

    vm.determineStartState = function () {
        if (stateHolder.AeUser.applications.length) {
            vm.resource = Number($location.search().resource);

            if (!vm.resource){
                var cookieResource = $cookies.getObject('resource');
                console.log('cookieResource', cookieResource);

                if (cookieResource) {
                    vm.resource = cookieResource;
                }
                else{
                    vm.resource = stateHolder.AeUser.applications[0].resource_id;
                }
            }
        }

        var timespan = $location.search().timespan;

        if(_.has(vm.timeOptions, timespan)){
            vm.timeSpan = vm.timeOptions[timespan];
        }
        else{
            vm.timeSpan = vm.timeOptions['1h'];
        }

        var graphType = $location.search().graphtype;
        if(!graphType){
            vm.graphType = {selected: 'metrics_graphs'};
        }
        else{
            vm.graphType = {selected: graphType};
        }
        vm.updateSearchParams();
    };

    vm.updateSearchParams = function () {
        $location.search('resource', vm.resource);
        $location.search('timespan', vm.timeSpan.key);
        $location.search('graphtype', vm.graphType.selected);
        stateHolder.resource = vm.resource;

        if (vm.resource){
            $cookies.putObject('resource', vm.resource,
                {expires:new Date(3000, 1, 1)});
        }
        vm.refreshData();
    };

    vm.refreshData = function () {
        vm.fetchApdexStats();
        vm.fetchTrendingReports();
        vm.fetchMetrics();
        vm.fetchRequestsBreakdown();
        vm.fetchSlowCalls();
    };

    vm.changedTimeSpan = function(){
        vm.startDateFilter = timeSpanToStartDate(vm.timeSpan.key);
        vm.refreshData();
    };

    vm.intervalId = $interval(function () {
        if (_.contains(['30m', "1h"], vm.timeSpan.key)) {
            // don't do anything if window is unfocused
            if(document.hidden === true){
                return ;
            }
            vm.refreshData();
        }
    }, 60000);

    vm.fetchApdexStats = function () {
        vm.loading.apdex = true;
        vm.apdexStats = applicationsPropertyResource.query({
                'key': 'apdex_stats',
                'resourceId': vm.resource,
                "start_date": timeSpanToStartDate(vm.timeSpan.key)
            },
            function (data) {
                vm.loading.apdex = false;

                vm.exceptions = _.reduce(data, function (memo, row) {
                    return memo + row.errors;
                }, 0);
                vm.satisfyingRequests = _.reduce(data, function (memo, row) {
                    return memo + row.satisfying_requests;
                }, 0);
                vm.toleratedRequests = _.reduce(data, function (memo, row) {
                    return memo + row.tolerated_requests;
                }, 0);
                vm.frustratingRequests = _.reduce(data, function (memo, row) {
                    return memo + row.frustrating_requests;
                }, 0);
                if (data.length) {
                    vm.uptimeStats = data[0].uptime;
                }

            },
            function () {
                vm.loading.apdex = false;
            }
        );
    }

    vm.fetchMetrics = function () {
        vm.loading.series = true;
        applicationsPropertyResource.query({
            'resourceId': vm.resource,
            'key': vm.graphType.selected,
            "start_date": timeSpanToStartDate(vm.timeSpan.key)
        }, function (data) {
            if (vm.graphType.selected == 'metrics_graphs') {
                vm.metricsChartData = {
                    json: data,
                    xFormat: '%Y-%m-%dT%H:%M:%S',
                    keys: {
                        x: 'x',
                        value: ["main", "sql", "nosql", "tmpl", "remote", "custom"]
                    },
                    names: {
                        main: 'View/Application logic',
                        sql: 'Relational database queries',
                        nosql: 'NoSql datastore calls',
                        tmpl: 'Template rendering',
                        custom: 'Custom timed calls',
                        remote: 'Requests to remote resources'
                    },
                    type: 'area',
                    groups: [["main", "sql", "nosql", "remote", "custom", "tmpl"]],
                    order: null
                };
            }
            else if (vm.graphType.selected == 'report_graphs') {
                vm.reportChartData = {
                    json: data,
                    xFormat: '%Y-%m-%dT%H:%M:%S',
                    keys: {
                        x: 'x',
                        value: ["not_found", "report"]
                    },
                    names: {
                        report: 'Errors',
                        not_found: '404\'s requests'
                    },
                    type: 'bar'
                };
            }
            else if (vm.graphType.selected == 'slow_report_graphs') {
                vm.reportSlowChartData = {
                    json: data,
                    xFormat: '%Y-%m-%dT%H:%M:%S',
                    keys: {
                        x: 'x',
                        value: ["slow_report"]
                    },
                    names: {
                        slow_report: 'Slow reports'
                    },
                    type: 'bar'
                };
            }
            else if (vm.graphType.selected == 'response_graphs') {
                vm.responseChartData = {
                    json: data,
                    xFormat: '%Y-%m-%dT%H:%M:%S',
                    keys: {
                        x: 'x',
                        value: ["today", "days_ago_2", "days_ago_7"]
                    },
                    names: {
                        today: 'Today',
                        "days_ago_2": '2 days ago',
                        "days_ago_7": '7 days ago'
                    }
                };
            }
            else if (vm.graphType.selected == 'requests_graphs') {
                vm.requestsChartData = {
                    json: data,
                    xFormat: '%Y-%m-%dT%H:%M:%S',
                    keys: {
                        x: 'x',
                        value: ["requests"]
                    },
                    names: {
                        requests: 'Requests/s'
                    }
                };
            }
            vm.loading.series = false;
        }, function(){
            vm.loading.series = false;
        });
    }

    vm.fetchSlowCalls = function () {
        vm.loading.slowCalls = true;
        applicationsPropertyResource.query({
            'resourceId': vm.resource,
            "start_date": timeSpanToStartDate(vm.timeSpan.key),
            'key': 'slow_calls'
        }, function (data) {
            vm.slowCalls = data;
            vm.loading.slowCalls = false;
        }, function () {
            vm.loading.slowCalls = false;
        });
    }

    vm.fetchRequestsBreakdown = function () {
        vm.loading.requestsBreakdown = true;
        applicationsPropertyResource.query({
            'resourceId': vm.resource,
            "start_date": timeSpanToStartDate(vm.timeSpan.key),
            'key': 'requests_breakdown'
        }, function (data) {
            vm.requestsBreakdown = data;
            vm.loading.requestsBreakdown = false;
        }, function () {
            vm.loading.requestsBreakdown = false;
        });
    }

    vm.fetchTrendingReports = function () {

        if (vm.graphType.selected == 'slow_report_graphs') {
            var report_type = 'slow';
        }
        else {
            var report_type = 'error';
        }

        vm.loading.reports = true;
        vm.trendingReports = applicationsPropertyResource.query({
                'key': 'trending_reports',
                'resourceId': vm.resource,
                "start_date": timeSpanToStartDate(vm.timeSpan.key),
                "report_type": report_type
            },
            function () {
                vm.loading.reports = false;
            },
            function () {
                vm.loading.reports = false;
            }
        );
    };

    $scope.$on('$destroy',function(){
        $interval.cancel(vm.intervalId);
    });

    if (stateHolder.AeUser.applications.length){
        vm.show_dashboard = true;
        vm.determineStartState();
        vm.refreshData();
    }
}
