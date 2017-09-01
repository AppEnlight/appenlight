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

angular.module('appenlight.services.chartResultParser',[]).factory('chartResultParser', function () {

    function transform(data) {

        /** transform result to a format that is more friendly
         *  to c3js we don't want to export this way as default
         *  as TSV stuff is less readable overall
         *
         * we want format of:
         * {x: [unix_timestamps],
         * key1: [val,list],
         * key2: [val,list]...}
         *
         *  OR
         *
         * handle special case where we want pie/donut for
         * aggregation with a single metric, we need to transform
         * the data from:
         * [y:list, categories:[cat1,cat2,...]]
         * to
         * [cat1: val, cat2:val...] format to render properly
         */
        var chartC3Config = {
            data: {
                json: [],
                type: 'bar'
            },
            point: {
                show: false
            },
            tooltip: {
                format: {
                    title: function (d) {
                        if (d) {
                            return '' + d;
                        }
                        return '';
                    },
                    value: function (value, ratio, id, index) {
                        return d3.round(value, 3);
                    }
                }
            },
            regions: data.rect_regions
        };
        var labels = _.keys(data.system_labels);
        var specialCases = ['pie', 'donut', 'gauge'];
        if (labels.length === 1 && _.contains(specialCases,
                data.chart_type.type)) {
            var transformedData = {};

            _.each(data.series, function (item) {
                transformedData[item['key']] = item[labels[0]];
            });
        }
        else {
            var transformedData = {'key': []};

            _.each(labels, function (label) {
                transformedData[label] = [];
            });

            _.each(data.series, function (item) {
                for (key in item) {
                    transformedData[key].push(item[key])
                }
            });
        }


        if (data.parent_agg.type === 'time_histogram') {
            chartC3Config.axis = {
                x: {
                    type: 'timeseries',
                    tick: {
                        format: '%Y-%m-%d'
                    }
                }
            };
            chartC3Config.data.xFormat = '%Y-%m-%dT%H:%M:%S';
        }
        else if (data.categories) {
            chartC3Config.axis = {
                x: {
                    type: 'category',
                    categories: data.categories
                }
            };
            // we don't want to show key as label if it is being
            // used as a category instead
            if (data.categories) {
                delete transformedData['key'];
            }
        }

        var human_labels = {};
        _.each(_.pairs(data.system_labels), function(entry){
           human_labels[entry[0]] = entry[1].human_label;
        });
        var chartC3Data = {
            json: transformedData,
            names: human_labels,
            groups: data.groups,
            type: data.chart_type.type
        };

        if (data.parent_agg.type == 'time_histogram') {
            chartC3Data.x = 'key';
        }
        return {chartC3Data: chartC3Data, chartC3Config: chartC3Config}
    }

    return transform
});
