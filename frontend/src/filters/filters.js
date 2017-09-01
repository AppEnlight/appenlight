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

'use strict';

/* Filters */

angular.module('appenlight.filters').
    filter('interpolate', ['version', function (version) {
        return function (text) {
            return String(text).replace(/\%VERSION\%/mg, version);
        }
    }])
    .filter('isoToRelativeTime', function () {
        return function (input) {
            return moment.utc(input).fromNow();
        }
    })

    .filter('round', function () {
        return function (input, precision) {
            return input.toFixed(precision)
        }
    })

    .filter('numberToThousands', function () {
        return function (input) {
            if (input > 1000000) {
                var i = input / 1000000;
                return i.toFixed(1).toString() + 'M'
            }
            else if (input > 1000) {
                var i = input / 1000;
                return i.toFixed(1).toString() + 'k'
            }
            else {
                return input;
            }
        }
    })
    .filter('getOrdered', function () {
        return function (input, filterOn) {
            var ordered = {};
            for (var key in input) {
                ordered[input[key][filterOn]] = input[key];
            }
            return ordered;
        };
    })
    .filter('objectToOrderedArray', function(){
        return function(items, field, reverse) {
            var filtered = [];
            angular.forEach(items, function(item) {
                filtered.push(item);
            });
            filtered.sort(function (a, b) {
                return (a[field] > b[field] ? 1 : -1);
            });
            if(reverse) filtered.reverse();
            return filtered;
        };
    })
    .filter('apdexValue', function () {
        return function (input) {
            if (input.apdex >= 95) {
                return 'satisfactory';
            } else if (input.apdex >= 80) {
                return 'tolerating';
            } else {
                return 'frustrating';
            }
        };
    })
    .filter('truncate', function(){
        return function (text, length, end) {
            if (isNaN(length))
                length = 10;

            if (end === undefined)
                end = "...";

            if (text.length <= length || text.length - end.length <= length) {
                return text;
            }
            else {
                return String(text).substring(0, length-end.length) + end;
            }

        };
    })

;
