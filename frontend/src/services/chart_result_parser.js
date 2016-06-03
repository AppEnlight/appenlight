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
