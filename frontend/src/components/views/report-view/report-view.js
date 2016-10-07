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

angular.module('appenlight.components.reportView', [])
    .component('reportView', {
        templateUrl: 'components/views/report-view/report-view.html',
        controller: ReportViewController
    });

ReportViewController.$inject = ['$window', '$location', '$state', '$uibModal',
    '$cookies', 'reportGroupPropertyResource', 'reportGroupResource',
    'logsNoIdResource', 'stateHolder'];

function ReportViewController($window, $location, $state, $uibModal, $cookies, reportGroupPropertyResource, reportGroupResource, logsNoIdResource, stateHolder) {
    var vm = this;
    vm.window = $window;
    vm.stateHolder = stateHolder;
    vm.$state = $state;
    vm.reportHistoryConfig = {
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
    vm.mentionedPeople = [];
    vm.reportHistoryData = {};
    vm.textTraceback = true;
    vm.rawTraceback = '';
    vm.traceback = '';
    vm.reportType = 'report';
    vm.report = null;
    vm.showLong = false;
    vm.reportLogs = null;
    vm.requestStats = null;
    vm.comment = null;
    vm.is_loading = {
        report: true,
        logs: true,
        history: true
    };

    vm.searchMentionedPeople = function(term){
        //vm.mentionedPeople = [];
        var term = term.toLowerCase();
        reportGroupPropertyResource.get({
                groupId: vm.report.group_id,
                key: 'assigned_users'
            }, null,
            function (data) {
                var users = [];
                _.each(data.assigned, function(u){
                    users.push({label: u.user_name});
                });
                _.each(data.unassigned, function(u){
                    users.push({label: u.user_name});
                });

                var result = _.filter(users, function(u){
                   return u.label.toLowerCase().indexOf(term) !== -1;
                });
                vm.mentionedPeople = result;
            });
    };

    vm.searchTag = function (tag, value) {
        console.log(tag, value);
        if (vm.report.report_type === 3) {
            $location.url($state.href('report.list_slow'));
        }
        else {
            $location.url($state.href('report.list'));
        }
        $location.search(tag, value);
    };

    vm.tabs = {
        slow_calls:false,
        request_details:false,
        logs:false,
        comments:false,
        affected_users:false
    };
    if ($cookies.selectedReportTab) {
        vm.tabs[$cookies.selectedReportTab] = true;
    }
    else{
        $cookies.selectedReportTab = 'request_details';
        vm.tabs.request_details = true;
    }

    vm.fetchLogs = function () {
        if (!vm.report.request_id){
            return
        }
        vm.is_loading.logs = true;
        logsNoIdResource.query({request_id: vm.report.request_id},
            function (data) {
            vm.is_loading.logs = false;
            vm.reportLogs = data;
        }, function () {
            vm.is_loading.logs = false;
        });
    };
    vm.addComment = function () {
        reportGroupPropertyResource.save({
                groupId: vm.report.group_id,
                key: 'comments'
            }, {body: vm.comment},
            function (data) {
                vm.report.comments.push(data);
            });
        vm.comment = '';
    };

    vm.fetchReport = function () {
        vm.is_loading.report = true;
        reportGroupResource.get($state.params, function (data) {
            vm.is_loading.report = false;
            if (data.request) {
                try {
                    var to_sort = _.pairs(data.request);
                    data.request = _.object(_.sortBy(to_sort, function (i) {
                        return i[0]
                    }));
                }
                catch (err) {
                }
            }
            vm.report = data;
            if (vm.report.req_stats) {
                vm.requestStats = [];
                _.each(_.pairs(vm.report.req_stats['percentages']), function (p) {
                    vm.requestStats.push({
                        name: p[0],
                        value: vm.report.req_stats[p[0]].toFixed(3),
                        percent: p[1],
                        calls: vm.report.req_stats[p[0] + '_calls']
                    })
                });
            }
            vm.traceback = data.traceback;
            _.each(vm.traceback, function (frame) {
                if (frame.line) {
                    vm.rawTraceback += 'File ' + frame.file + ' line ' + frame.line + ' in ' + frame.fn + ": \r\n";
                }
                vm.rawTraceback += '    ' + frame.cline + "\r\n";
            });

            if (stateHolder.AeUser.id){
                vm.fetchHistory();
            }

            vm.selectedTab($cookies.selectedReportTab);

        }, function (response) {
            console.log(response);
            if (response.status == 403) {
                var uid = response.headers('x-appenlight-uid');
                if (!uid) {
                    window.location = '/register?came_from=' + encodeURIComponent(window.location);
                }
            }
            vm.is_loading.report = false;
        });
    };

    vm.selectedTab = function(tab_name){
        $cookies.selectedReportTab = tab_name;
        if (tab_name == 'logs' && vm.reportLogs === null) {
            vm.fetchLogs();
        }
    };

    vm.markFixed = function () {
        reportGroupResource.update({
                groupId: vm.report.group_id
            }, {fixed: !vm.report.group.fixed},
            function (data) {
                vm.report.group.fixed = data.fixed;
            });
    };

    vm.markPublic = function () {
        reportGroupResource.update({
                groupId: vm.report.group_id
            }, {public: !vm.report.group.public},
            function (data) {
                vm.report.group.public = data.public;
            });
    };

    vm.delete = function () {
        reportGroupResource.delete({'groupId': vm.report.group_id},
            function (data) {
            $state.go('report.list');
        })
    };

    vm.assignUsersModal = function (index) {
        vm.opts = {
            backdrop: 'static',
            templateUrl: 'AssignReportCtrl.html',
            controller: 'AssignReportCtrl as ctrl',
            resolve: {
                report: function () {
                    return vm.report;
                }
            }
        };
        var modalInstance = $uibModal.open(vm.opts);
        modalInstance.result.then(function (report) {

        }, function () {
            console.info('Modal dismissed at: ' + new Date());
        });

    };

    vm.fetchHistory = function () {
        reportGroupPropertyResource.query({
            groupId: vm.report.group_id,
            key: 'history'
        }, function (data) {
            vm.reportHistoryData = {
                json: data,
                keys: {
                    x: 'x',
                    value: ["reports"]
                },
                names: {
                    reports: 'Reports history'
                },
                type: 'bar'
            };
            vm.is_loading.history = false;
        });
    };

    vm.nextDetail = function () {
        $state.go('report.view_detail', {
            groupId: vm.report.group_id,
            reportId: vm.report.group.next_report
        });
    };
    vm.previousDetail = function () {
        $state.go('report.view_detail', {
            groupId: vm.report.group_id,
            reportId: vm.report.group.previous_report
        });
    };

    vm.runIntegration = function (integration_name) {
        console.log(integration_name);
        if (integration_name == 'bitbucket') {
            var controller = 'BitbucketIntegrationCtrl as ctrl';
            var template_url = 'templates/integrations/bitbucket.html';
        }
        else if (integration_name == 'github') {
            var controller = 'GithubIntegrationCtrl as ctrl';
            var template_url = 'templates/integrations/github.html';
        }
        else if (integration_name == 'jira') {
            var controller = 'JiraIntegrationCtrl as ctrl';
            var template_url = 'templates/integrations/jira.html';
        }
        else {
            return false;
        }

        vm.opts = {
            backdrop: 'static',
            templateUrl: template_url,
            controller: controller,
            resolve: {
                integrationName: function () {
                    return integration_name
                },
                report: function () {
                    return vm.report;
                }
            }
        };
        var modalInstance = $uibModal.open(vm.opts);
        modalInstance.result.then(function (report) {

        }, function () {
            console.info('Modal dismissed at: ' + new Date());
        });

    };

    // load report
    vm.fetchReport();


}
