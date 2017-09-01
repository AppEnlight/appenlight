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

// This code is inspired by https://github.com/jettro/c3-angular-sample/tree/master/js
// License is MIT


angular.module('appenlight.directives.c3chart', [])
    .controller('ChartCtrl', ['$scope', '$timeout', function ($scope, $timeout) {
        $scope.chart = null;
        this.showGraph = function () {
            var config = angular.copy($scope.config);
            var firstLoad = true;
            config.bindto = "#" + $scope.domid;
            var originalXTickCount = null;
            if ($scope.data && $scope.config) {
                if (!_.isEmpty($scope.data)) {
                    _.extend(config.data, angular.copy($scope.data));
                }
                console.log('ChartCtrl.showGraph', config);
                config.onresized = function () {
                    if (this.currentWidth < 400){
                        $scope.chart.internal.config.axis_x_tick_culling_max = 3;
                    }
                    else if (this.currentWidth < 600){
                        $scope.chart.internal.config.axis_x_tick_culling_max = 5;
                    }
                    else{
                        $scope.chart.internal.config.axis_x_tick_culling_max = originalXTickCount;
                    }
                    $scope.chart.flush();
                };


                $scope.chart = c3.generate(config);
                originalXTickCount = $scope.chart.internal.config.axis_x_tick_culling_max;
                $scope.chart.internal.config.onresized.call($scope.chart.internal);
            }
            console.log('should update', $scope.update);
            if ($scope.update) {
                console.log('reload driven');
                $scope.$watch('data', function () {
                    if (!firstLoad) {
                        console.log('data updated', $scope.data);
                        $scope.chart.load(angular.copy($scope.data), {unload: true});
                        if (typeof $scope.data.groups != 'undefined') {
                            console.log('add groups');
                            $scope.chart.groups($scope.data.groups);
                        }
                        if (typeof $scope.data.names != 'undefined') {
                            console.log('add names');
                            $scope.chart.data.names($scope.data.names);
                        }
                        $scope.chart.flush();
                    }
                }, true);
            }
            $scope.$watch('config.regions', function (newValue, oldValue) {
                if (newValue === oldValue) {
                    return
                }
                if (typeof $scope.config.regions != 'undefined') {
                    console.log('update regions', $scope.config.regions);
                    $scope.chart.regions($scope.config.regions);
                }
            });

            firstLoad = false;
            $scope.$watch('resizetrigger', function (newValue, oldValue) {
                if (newValue !== oldValue) {
                    $timeout(function () {
                        $scope.chart.resize();
                        $scope.chart.internal.config.onresized.call($scope.chart.internal);
                    });
                }
            });
        };
    }])
    .directive('c3chart', function ($timeout) {
        var chartLinker = function (scope, element, attrs, chartCtrl) {
            // Trick to wait for all rendering of the DOM to be finished.
            // then we can tell c3js to "connect" to our dom node
            $timeout(function () {
                chartCtrl.showGraph()
            });

            scope.$on("$destroy", function () {
                    if (scope.chart !== null) {
                        scope.chart = scope.chart.destroy();
                        delete element;
                        delete scope.chart;
                    }
                }
            );
        };
        return {
            "restrict": "E",
            "controller": "ChartCtrl",
            "scope": {
                "domid": "@domid",
                "config": "=config",
                "data": "=data",
                "resizetrigger": "=resizetrigger",
                "update": "=update"
            },
            "template": "<div id='{{domid}}' class='chart'></div>",
            "replace": true,
            "link": chartLinker
        }
    });
